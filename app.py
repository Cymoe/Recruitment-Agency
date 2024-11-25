import streamlit as st
import asyncio
import os
from datetime import datetime
from pathlib import Path
from streamlit_option_menu import option_menu
from agents.orchestrator import OrchestratorAgent
from utils.logger import setup_logger
from utils.exceptions import ResumeProcessingError

# Initialize logger
logger = setup_logger()

# Configure Streamlit page
st.set_page_config(
    page_title="AI Recruiter Agency",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

async def process_resume(file_path: str) -> dict:
    """Process resume through the AI recruitment pipeline"""
    try:
        orchestrator = OrchestratorAgent()
        resume_data = {
            "file_path": file_path,
            "submission_timestamp": datetime.now().isoformat(),
        }
        return await orchestrator.process_application(resume_data)
    except Exception as e:
        logger.error(f"Error processing resume: {str(e)}")
        raise

def save_uploaded_file(uploaded_file) -> str:
    """Save uploaded file and return the file path"""
    try:
        # Create uploads directory if it doesn't exist
        save_dir = Path("uploads")
        save_dir.mkdir(exist_ok=True)

        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = save_dir / f"resume_{timestamp}_{uploaded_file.name}"

        # Save the file
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        return str(file_path)
    except Exception as e:
        st.error(f"Error saving file: {str(e)}")
        raise

def main():
    # Sidebar navigation
    with st.sidebar:
        st.image(
            "https://img.icons8.com/resume",
            width=50,
        )
        st.title("AI Recruiter Agency")
        selected = option_menu(
            menu_title="Navigation",
            options=["Upload Resume", "About"],
            icons=["cloud-upload", "info-circle"],
            menu_icon="cast",
            default_index=0,
        )

    if selected == "Upload Resume":
        st.header("📄 Resume Analysis")
        st.write("Upload a resume to get AI-powered insights and job matches.")

        uploaded_file = st.file_uploader(
            "Choose a PDF resume file",
            type=["pdf"],
            help="Upload a PDF resume to analyze",
        )

        if uploaded_file:
            try:
                with st.spinner("Saving uploaded file..."):
                    file_path = save_uploaded_file(uploaded_file)

                st.info("Resume uploaded successfully! Processing...")

                # Create placeholder for progress bar
                progress_bar = st.progress(0)
                status_text = st.empty()

                # Process resume
                try:
                    status_text.text("Analyzing resume...")
                    progress_bar.progress(25)

                    # Run analysis asynchronously
                    result = asyncio.run(process_resume(file_path))

                    if result["status"] == "completed":
                        progress_bar.progress(100)
                        status_text.text("Analysis complete!")

                        # Display results in tabs
                        tab1, tab2, tab3, tab4 = st.tabs(
                            [
                                "📊 Analysis",
                                "💼 Job Matches",
                                "🎯 Screening",
                                "💡 Recommendation",
                            ]
                        )

                        with tab1:
                            st.subheader("Skills Analysis")
                            analysis = eval(result["analysis_results"]["analysis"])
                            
                            # Display technical skills
                            st.write("**Technical Skills:**")
                            if "technical_skills" in analysis:
                                for skill in analysis["technical_skills"]:
                                    st.write(f"- {skill}")
                            
                            # Display experience level
                            if "experience_level" in analysis:
                                st.metric("Experience Level", analysis["experience_level"])
                            
                            # Display education
                            if "education_level" in analysis:
                                st.metric("Education Level", analysis["education_level"])

                        with tab2:
                            st.subheader("Matched Positions")
                            matches = eval(result["job_matches"]["matches"])
                            
                            if not matches:
                                st.warning("No suitable positions found.")
                            else:
                                for match in matches:
                                    with st.container():
                                        col1, col2 = st.columns([2, 1])
                                        with col1:
                                            st.write(f"**Job ID:** {match['job_id']}")
                                            st.write(f"**Reasoning:** {match['reasoning']}")
                                            st.write("**Key Matches:**")
                                            for skill in match['key_matches']:
                                                st.write(f"- {skill}")
                                        with col2:
                                            st.metric("Match Score", f"{match['match_score']}%")
                                            if match.get('gaps'):
                                                st.write("**Skill Gaps:**")
                                                for gap in match['gaps']:
                                                    st.write(f"- {gap}")
                                    st.divider()

                        with tab3:
                            st.subheader("Screening Results")
                            screening = eval(result["screening_results"]["screening_report"])
                            
                            # Display qualification alignment
                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric("Qualification Score", 
                                        f"{screening['qualification_alignment']['score']}%")
                                st.write(screening['qualification_alignment']['analysis'])
                            with col2:
                                st.metric("Experience Score", 
                                        f"{screening['experience_relevance']['score']}%")
                                st.write(screening['experience_relevance']['analysis'])
                            
                            # Display skill match
                            st.subheader("Skill Assessment")
                            st.metric("Skill Match Score", f"{screening['skill_match']['score']}%")
                            col3, col4 = st.columns(2)
                            with col3:
                                st.write("**Strengths:**")
                                for strength in screening['skill_match']['strengths']:
                                    st.write(f"- {strength}")
                            with col4:
                                st.write("**Areas for Development:**")
                                for gap in screening['skill_match']['gaps']:
                                    st.write(f"- {gap}")
                            
                            # Display red flags if any
                            if screening['red_flags']:
                                st.warning("**Potential Concerns:**")
                                for flag in screening['red_flags']:
                                    st.write(f"- {flag}")

                        with tab4:
                            st.subheader("Final Recommendation")
                            recommendation = eval(result["final_recommendation"]["final_recommendation"])
                            
                            # Display summary
                            st.write("### Summary")
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write("**Strengths:**")
                                for strength in recommendation['summary']['candidate_strengths']:
                                    st.write(f"- {strength}")
                            with col2:
                                st.write("**Development Areas:**")
                                for area in recommendation['summary']['development_areas']:
                                    st.write(f"- {area}")
                            
                            # Display hiring recommendation
                            st.write("### Hiring Recommendation")
                            decision = recommendation['hiring_recommendation']['decision']
                            if decision in ["Strongly Recommend", "Recommend"]:
                                st.success(decision)
                            elif decision == "Consider":
                                st.warning(decision)
                            else:
                                st.error(decision)
                            st.write(recommendation['hiring_recommendation']['rationale'])
                            
                            # Display next steps
                            st.write("### Next Steps")
                            for step in recommendation['recommendations']['immediate_next_steps']:
                                st.write(f"- {step}")

                        # Save results
                        output_dir = Path("results")
                        output_dir.mkdir(exist_ok=True)
                        output_file = (
                            output_dir
                            / f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                        )

                        with open(output_file, "w") as f:
                            f.write(str(result))

                        st.success(
                            f"Analysis completed! Results saved to {output_file}",
                            icon="✅",
                        )

                except Exception as e:
                    st.error(f"Error processing resume: {str(e)}")
                    logger.error(f"Error processing resume: {str(e)}")

                finally:
                    # Clean up uploaded file
                    try:
                        os.remove(file_path)
                    except Exception as e:
                        logger.error(f"Error removing temporary file: {str(e)}")

            except Exception as e:
                st.error(f"Error handling file upload: {str(e)}")
                logger.error(f"Error handling file upload: {str(e)}")

    elif selected == "About":
        st.header("About AI Recruiter Agency")
        st.write(
            """
            AI Recruiter Agency is an advanced resume analysis and job matching system 
            powered by artificial intelligence. Our system:

            - 📄 Extracts and analyzes resume content
            - 🎯 Matches candidates with suitable positions
            - 📊 Provides detailed skills analysis
            - 💡 Offers personalized recommendations
            """
        )

if __name__ == "__main__":
    # Run Streamlit
    main()

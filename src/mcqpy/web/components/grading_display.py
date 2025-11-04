"""
Grading display component for MCQPy web interface
"""

import streamlit as st
import pandas as pd
from typing import List
from mcqpy.grade.utils import GradedSet
from mcqpy.grade import get_grade_dataframe
import numpy as np


class GradingDisplayComponent:
    """Component for displaying grading results and analysis"""
    
    def show_results(self, graded_sets: List[GradedSet]):
        """Display grading results with detailed breakdown"""
        
        if not graded_sets:
            st.warning("No grading results to display.")
            return
        
        # Summary statistics
        self._show_summary_stats(graded_sets)
        
        # Individual results
        with st.expander("👥 View Individual Student Results"):
            st.subheader("📋 Individual Results")
            self._show_individual_results(graded_sets)
        
        # Download options
        st.subheader("💾 Download Results")
        self._show_download_options(graded_sets)
        
        # Detailed question analysis
        with st.expander("📊 Question Analysis"):
            self._show_question_analysis(graded_sets)
    
    def _show_summary_stats(self, graded_sets: List[GradedSet]):
        """Display summary statistics"""
        
        st.subheader("📈 Summary Statistics")
        
        total_students = len(graded_sets)
        total_points = [gs.points for gs in graded_sets]
        max_points = graded_sets[0].max_points if graded_sets else 0
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Students Graded", total_students)
        
        with col2:
            avg_score = sum(total_points) / len(total_points) if total_points else 0
            st.metric("Average Score", f"{avg_score:.1f} / {max_points}")
        
        with col3:
            avg_percentage = (avg_score / max_points * 100) if max_points > 0 else 0
            st.metric("Average %", f"{avg_percentage:.1f}%")
        
        with col4:
            highest_score = max(total_points) if total_points else 0
            st.metric("Highest Score", f"{highest_score} / {max_points}")
        
        # Score distribution chart
        if len(graded_sets) > 1:
            st.subheader("📊 Score Distribution")
            
            # Create DataFrame for plotting
            df_scores = pd.DataFrame({
                'Student': [gs.student_name or gs.student_id for gs in graded_sets],
                'Score': total_points,
                'Percentage': [(score / max_points * 100) if max_points > 0 else 0 for score in total_points]
            })

            hist, bins = np.histogram(df_scores['Score'], bins='auto')
            df_hist = pd.DataFrame({
                'Score Range': [f"{bins[i]:.1f} - {bins[i+1]:.1f}" for i in range(len(bins)-1)],
                'Count': hist
            })
            st.bar_chart(df_hist.set_index('Score Range')['Count'])
            # Bar chart
            # st.bar_chart(df_scores.set_index('Student')['Percentage'])


    
    def _show_individual_results(self, graded_sets: List[GradedSet]):
        """Display individual student results"""
        
        for i, graded_set in enumerate(graded_sets):
            with st.expander(f"👤 {graded_set.student_name or graded_set.student_id} - {graded_set.points}/{graded_set.max_points} ({graded_set.points/graded_set.max_points*100:.1f}%)"):
                
                # Student info
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Name:** {graded_set.student_name}")
                with col2:
                    st.write(f"**ID:** {graded_set.student_id}")
                
                # Question-by-question breakdown
                if graded_set.graded_questions:
                    st.write("**Question Breakdown:**")
                    
                    question_data = []
                    for q in graded_set.graded_questions:
                        status = "✅" if q.point_value == q.max_point_value else "❌"
                        question_data.append({
                            "Question": q.qid,
                            "Status": status,
                            "Points": f"{q.point_value}/{q.max_point_value}",
                            "Student Answer": self._format_answer(q.student_answers),
                            "Correct Answer": self._format_answer(q.correct_answers)
                        })
                    
                    df_questions = pd.DataFrame(question_data)
                    st.dataframe(df_questions, width='content', hide_index=True)
    
    def _show_download_options(self, graded_sets: List[GradedSet]):
        """Show download options for results"""
        
        # Generate grade dataframe
        df = get_grade_dataframe(graded_sets)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # CSV download
            csv = df.to_csv(index=False)
            st.download_button(
                label="📄 Download as CSV",
                data=csv,
                file_name="mcqpy_grades.csv",
                mime="text/csv",
                width='content',
                key="csv_download"
            )
        
        with col2:
            # Excel download
            from io import BytesIO
            buffer = BytesIO()
            df.to_excel(buffer, index=False, engine='openpyxl')
            excel_data = buffer.getvalue()
            
            st.download_button(
                label="📊 Download as Excel",
                data=excel_data,
                file_name="mcqpy_grades.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                width='content',
                key="excel_download"
            )
        
        # Preview the data
        with st.expander("Preview Data"):
            st.dataframe(df, width='content')
    
    def _show_question_analysis(self, graded_sets: List[GradedSet]):
        """Show detailed question analysis"""
        
        if not graded_sets or not graded_sets[0].graded_questions:
            st.warning("No question data available for analysis.")
            return
        
        # Collect question statistics
        question_stats = {}
        
        for graded_set in graded_sets:
            for q in graded_set.graded_questions:
                if q.qid not in question_stats:
                    question_stats[q.qid] = {
                        'correct': 0,
                        'total': 0,
                        'max_points': q.max_point_value
                    }
                
                question_stats[q.qid]['total'] += 1
                if q.point_value == q.max_point_value:
                    question_stats[q.qid]['correct'] += 1
        
        # Display question statistics
        question_data = []
        for qid, stats in question_stats.items():
            success_rate = (stats['correct'] / stats['total']) * 100 if stats['total'] > 0 else 0
            question_data.append({
                'Question ID': qid,
                'Correct Answers': stats['correct'],
                'Total Attempts': stats['total'],
                'Success Rate (%)': f"{success_rate:.1f}%",
                'Difficulty': self._get_difficulty_level(success_rate)
            })
        
        df_analysis = pd.DataFrame(question_data)
        st.dataframe(df_analysis, width='content', hide_index=True)
        
        # Difficulty distribution
        difficulty_counts = df_analysis['Difficulty'].value_counts()
        st.bar_chart(difficulty_counts)
    
    def _format_answer(self, answer_list: List[int]) -> str:
        """Format answer list for display"""
        if not answer_list:
            return "None"
        return ", ".join([f"Option {i+1}" for i, val in enumerate(answer_list) if val == 1])
    
    def _get_difficulty_level(self, success_rate: float) -> str:
        """Determine difficulty level based on success rate"""
        if success_rate >= 80:
            return "Easy"
        elif success_rate >= 60:
            return "Medium"
        elif success_rate >= 40:
            return "Hard"
        else:
            return "Very Hard"
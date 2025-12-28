"""
Test suite for database service operations
Tests all CRUD operations for candidates, interviews, questions, and answers
"""
import pytest
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Add parent directory to path to import app module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load test environment
load_dotenv()

# Import database service functions
from app.services.database_service import (
    create_or_get_candidate,
    create_interview,
    complete_interview,
    save_questions,
    get_interview_questions,
    save_answer,
    get_interview,
    get_interview_results,
    get_all_interviews,
    get_answer_count,
    authenticate_admin,
)


class TestDatabaseService:
    """Test database operations"""
    
    @pytest.fixture
    def test_candidate_email(self):
        """Generate unique test email"""
        timestamp = datetime.now().timestamp()
        return f"test_{timestamp}@example.com"
    
    def test_create_candidate(self, test_candidate_email):
        """Test creating a new candidate"""
        candidate = create_or_get_candidate(
            email=test_candidate_email,
            first_name="Test",
            last_name="User"
        )
        
        assert candidate is not None
        assert candidate["email"] == test_candidate_email
        assert candidate["first_name"] == "Test"
        assert candidate["last_name"] == "User"
        assert "id" in candidate
        
        print(f"✓ Created candidate: {candidate['id']}")
    
    def test_get_existing_candidate(self, test_candidate_email):
        """Test retrieving existing candidate"""
        # Create first
        candidate1 = create_or_get_candidate(email=test_candidate_email)
        
        # Get same candidate
        candidate2 = create_or_get_candidate(email=test_candidate_email)
        
        assert candidate1["id"] == candidate2["id"]
        print(f"✓ Retrieved existing candidate: {candidate1['id']}")
    
    def test_create_interview(self, test_candidate_email):
        """Test creating an interview"""
        candidate = create_or_get_candidate(email=test_candidate_email)
        
        interview = create_interview(
            candidate_id=candidate["id"],
            role="Software Developer"
        )
        
        assert interview is not None
        assert interview["candidate_id"] == candidate["id"]
        assert interview["role_applied"] == "Software Developer"
        assert "id" in interview
        
        print(f"✓ Created interview: {interview['id']}")
        return interview["id"]
    
    def test_save_questions(self, test_candidate_email):
        """Test saving questions for an interview"""
        candidate = create_or_get_candidate(email=test_candidate_email)
        interview = create_interview(candidate["id"], "Data Analyst")
        
        questions = [
            "What is your experience with data analysis?",
            "Explain SQL joins.",
            "How do you handle missing data?"
        ]
        
        saved_questions = save_questions(
            interview_id=interview["id"],
            role="Data Analyst",
            questions=questions
        )
        
        assert len(saved_questions) == 3
        assert saved_questions[0]["content"] == questions[0]
        assert saved_questions[0]["question_order"] == 1
        
        print(f"✓ Saved {len(saved_questions)} questions")
        return interview["id"]
    
    def test_save_answer(self, test_candidate_email):
        """Test saving an answer with evaluation"""
        candidate = create_or_get_candidate(email=test_candidate_email)
        interview = create_interview(candidate["id"], "QA Engineer")
        
        questions = ["What is your testing experience?"]
        saved_questions = save_questions(interview["id"], "QA Engineer", questions)
        
        answer = save_answer(
            interview_id=interview["id"],
            question_id=saved_questions[0]["id"],
            transcript="I have 3 years of manual and automated testing experience.",
            score=4.0,
            feedback="Good answer with specific experience mentioned."
        )
        
        assert answer is not None
        assert answer["transcript"] == "I have 3 years of manual and automated testing experience."
        assert answer["score"] == 4.0
        assert answer["feedback"] == "Good answer with specific experience mentioned."
        
        print(f"✓ Saved answer with score: {answer['score']}")
    
    def test_complete_interview_flow(self, test_candidate_email):
        """Test complete interview flow from start to finish"""
        # 1. Create candidate
        candidate = create_or_get_candidate(
            email=test_candidate_email,
            first_name="Integration",
            last_name="Test"
        )
        print(f"✓ Step 1: Created candidate {candidate['id']}")
        
        # 2. Create interview
        interview = create_interview(candidate["id"], "Product Manager")
        interview_id = interview["id"]
        print(f"✓ Step 2: Created interview {interview_id}")
        
        # 3. Save questions
        questions = [
            "What is your product management experience?",
            "How do you prioritize features?",
            "Describe a successful product launch."
        ]
        saved_questions = save_questions(interview_id, "Product Manager", questions)
        print(f"✓ Step 3: Saved {len(saved_questions)} questions")
        
        # 4. Submit answers
        answers_data = [
            ("I have 5 years of PM experience leading cross-functional teams.", 4.5, "Excellent answer with specific details."),
            ("I use impact vs effort matrix and stakeholder feedback.", 4.0, "Good methodology mentioned."),
            ("Led the launch of mobile app with 100K users in first month.", 5.0, "Outstanding answer with metrics.")
        ]
        
        for idx, (transcript, score, feedback) in enumerate(answers_data):
            answer = save_answer(
                interview_id=interview_id,
                question_id=saved_questions[idx]["id"],
                transcript=transcript,
                score=score,
                feedback=feedback
            )
            print(f"✓ Step 4.{idx+1}: Saved answer {idx+1} with score {score}")
        
        # 5. Complete interview
        total_score = sum(score for _, score, _ in answers_data)
        complete_interview(interview_id, total_score)
        print(f"✓ Step 5: Completed interview with total score {total_score}")
        
        # 6. Get results
        results = get_interview_results(interview_id)
        assert results is not None
        assert results["statistics"]["total_questions"] == 3
        assert results["statistics"]["answers_submitted"] == 3
        assert results["statistics"]["total_score"] == total_score
        assert results["status"] == "completed"
        print(f"✓ Step 6: Retrieved results - Average score: {results['statistics']['average_score']}")
        
        print("\n✅ Complete interview flow test PASSED")
        return interview_id
    
    def test_get_all_interviews(self):
        """Test retrieving all interviews"""
        interviews = get_all_interviews(limit=10)
        
        assert interviews is not None
        assert isinstance(interviews, list)
        print(f"✓ Retrieved {len(interviews)} interviews")
    
    def test_admin_authentication(self):
        """Test admin authentication"""
        # Try invalid credentials
        result = authenticate_admin("invalid@example.com", "wrongpassword")
        assert result is None
        print("✓ Invalid credentials rejected")
        
        # Try valid credentials (if default admin exists)
        result = authenticate_admin("admin@example.com", "Admin@123456")
        if result:
            assert result["email"] == "admin@example.com"
            print("✓ Valid credentials accepted")
        else:
            print("⚠ Default admin not found - run database migration first")


def test_database_connection():
    """Test basic database connection"""
    from app.services.database_service import supabase
    
    try:
        # Try a simple query
        result = supabase.table("candidates").select("id").limit(1).execute()
        print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


if __name__ == "__main__":
    print("="*60)
    print("AI INTERVIEWER - DATABASE SERVICE TESTS")
    print("="*60)
    print()
    
    # Run connection test first
    if not test_database_connection():
        print("\n❌ Cannot proceed without database connection")
        print("Please check your SUPABASE_URL and SUPABASE_KEY in .env")
        exit(1)
    
    print("\nRunning pytest tests...\n")
    pytest.main([__file__, "-v", "-s"])

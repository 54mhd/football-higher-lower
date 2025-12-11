"""
Script to seed the database with football trivia questions.
Run this script once to populate the questions table.
"""

import asyncio
from sqlalchemy import insert

from .db import engine, Base, Question, async_session_maker


SAMPLE_QUESTIONS = [
    {
        "question_text": "Which country won the FIFA World Cup 2022?",
        "option_a": "France",
        "option_b": "Argentina",
        "option_c": "Brazil",
        "option_d": "Germany",
        "correct_answer": "B",
        "difficulty": "medium",
        "category": "World Cup",
    },
    {
        "question_text": "How many times has Cristiano Ronaldo won the Ballon d'Or?",
        "option_a": "5",
        "option_b": "7",
        "option_c": "3",
        "option_d": "6",
        "correct_answer": "A",
        "difficulty": "hard",
        "category": "Player Awards",
    },
    {
        "question_text": "Which team won the UEFA Champions League 2023?",
        "option_a": "Manchester City",
        "option_b": "Real Madrid",
        "option_c": "Bayern Munich",
        "option_d": "Paris Saint-Germain",
        "correct_answer": "A",
        "difficulty": "medium",
        "category": "Champions League",
    },
    {
        "question_text": "In which year was the FIFA World Cup first held?",
        "option_a": "1930",
        "option_b": "1950",
        "option_c": "1922",
        "option_d": "1940",
        "correct_answer": "A",
        "difficulty": "hard",
        "category": "World Cup",
    },
    {
        "question_text": "How many players are on the field per team in football?",
        "option_a": "9",
        "option_b": "10",
        "option_c": "11",
        "option_d": "12",
        "correct_answer": "C",
        "difficulty": "easy",
        "category": "Rules",
    },
    {
        "question_text": "Which country has won the most FIFA World Cups?",
        "option_a": "Germany",
        "option_b": "Italy",
        "option_c": "Brazil",
        "option_d": "France",
        "correct_answer": "C",
        "difficulty": "medium",
        "category": "World Cup",
    },
    {
        "question_text": "What is the duration of a standard football match?",
        "option_a": "80 minutes",
        "option_b": "90 minutes",
        "option_c": "100 minutes",
        "option_d": "75 minutes",
        "correct_answer": "B",
        "difficulty": "easy",
        "category": "Rules",
    },
    {
        "question_text": "Which Premier League team has won the most titles?",
        "option_a": "Arsenal",
        "option_b": "Manchester United",
        "option_c": "Chelsea",
        "option_d": "Liverpool",
        "correct_answer": "B",
        "difficulty": "medium",
        "category": "Premier League",
    },
    {
        "question_text": "What does VAR stand for in football?",
        "option_a": "Video Analysis Review",
        "option_b": "Video Assistant Referee",
        "option_c": "Verbal Assistance Review",
        "option_d": "Video Automated Reviewing",
        "correct_answer": "B",
        "difficulty": "easy",
        "category": "Rules",
    },
    {
        "question_text": "Which player has scored the most goals in international football history?",
        "option_a": "Pelé",
        "option_b": "Diego Maradona",
        "option_c": "Cristiano Ronaldo",
        "option_d": "Lionel Messi",
        "correct_answer": "C",
        "difficulty": "hard",
        "category": "Players",
    },
    {
        "question_text": "In which city is the Maracanã stadium located?",
        "option_a": "São Paulo",
        "option_b": "Salvador",
        "option_c": "Rio de Janeiro",
        "option_d": "Brasília",
        "correct_answer": "C",
        "difficulty": "medium",
        "category": "Stadiums",
    },
    {
        "question_text": "How many times has Barcelona won the UEFA Champions League?",
        "option_a": "3",
        "option_b": "4",
        "option_c": "5",
        "option_d": "6",
        "correct_answer": "C",
        "difficulty": "hard",
        "category": "Champions League",
    },
    {
        "question_text": "Which country hosted the 2014 FIFA World Cup?",
        "option_a": "South Africa",
        "option_b": "Brazil",
        "option_c": "Russia",
        "option_d": "Qatar",
        "correct_answer": "B",
        "difficulty": "medium",
        "category": "World Cup",
    },
    {
        "question_text": "What is the maximum number of substitutes allowed during a football match?",
        "option_a": "3",
        "option_b": "5",
        "option_c": "7",
        "option_d": "10",
        "correct_answer": "B",
        "difficulty": "medium",
        "category": "Rules",
    },
    {
        "question_text": "Which team won the first UEFA Champions League in 1956?",
        "option_a": "AC Milan",
        "option_b": "Real Madrid",
        "option_c": "Manchester United",
        "option_d": "Benfica",
        "correct_answer": "B",
        "difficulty": "hard",
        "category": "Champions League",
    },
    {
        "question_text": "How many times has Lionel Messi won the Ballon d'Or?",
        "option_a": "7",
        "option_b": "8",
        "option_c": "9",
        "option_d": "6",
        "correct_answer": "B",
        "difficulty": "hard",
        "category": "Player Awards",
    },
    {
        "question_text": "In football, what does 'offside' mean?",
        "option_a": "A player is too close to the sideline",
        "option_b": "A player is ahead of all opponents except goalkeeper and one other player",
        "option_c": "A player is on the wrong side of the field",
        "option_d": "A player has fouled the opponent",
        "correct_answer": "B",
        "difficulty": "hard",
        "category": "Rules",
    },
    {
        "question_text": "Which team is known as 'The Red Devils'?",
        "option_a": "Liverpool",
        "option_b": "Arsenal",
        "option_c": "Manchester United",
        "option_d": "Manchester City",
        "correct_answer": "C",
        "difficulty": "easy",
        "category": "Premier League",
    },
    {
        "question_text": "What is the diameter of a football goal circle (penalty area) in yards?",
        "option_a": "16 yards",
        "option_b": "18 yards",
        "option_c": "20 yards",
        "option_d": "22 yards",
        "correct_answer": "B",
        "difficulty": "hard",
        "category": "Rules",
    },
    {
        "question_text": "Which player won the Golden Ball at the 2022 FIFA World Cup?",
        "option_a": "Messi",
        "option_b": "Mbappé",
        "option_c": "Neymar",
        "option_d": "Grealish",
        "correct_answer": "A",
        "difficulty": "medium",
        "category": "World Cup",
    },
]


async def seed_questions():
    """Seed the database with sample questions."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_maker() as session:
        try:
            # Check if questions already exist
            from sqlalchemy import select
            result = await session.execute(select(Question))
            existing_questions = result.scalars().all()

            if len(existing_questions) > 0:
                print(f"Database already contains {len(existing_questions)} questions. Skipping seeding.")
                return

            # Insert sample questions
            for question_data in SAMPLE_QUESTIONS:
                question = Question(**question_data)
                session.add(question)

            await session.commit()
            print(f"Successfully seeded {len(SAMPLE_QUESTIONS)} questions!")

        except Exception as e:
            print(f"Error seeding database: {e}")
            await session.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(seed_questions())

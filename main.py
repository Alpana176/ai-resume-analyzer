from chatbot.bot import GeminiChatbot
from services.resume_loader import extract_text_from_pdf
from services.text_splitter import split_text
from services.vector_store import create_vector_store, retrieve_chunks


def run_resume_analyzer():
    bot = GeminiChatbot()

    print("📄 AI Resume Analyzer (type 'exit' to quit)\n")

    while True:
        job_role = input("Enter target job role:\n")
        if job_role.lower() == "exit":
            break

        file_path = input("\nEnter path to your resume PDF:\n")
        if file_path.lower() == "exit":
            break

        # ✅ Extract text
        resume_text = extract_text_from_pdf(file_path)

        if resume_text.startswith("ERROR"):
            print("⚠️ Could not read PDF:", resume_text)
            continue

        if resume_text.strip() == "":
            print("⚠️ Empty resume content detected\n")
            continue

        # ✅ RAG Pipeline
        chunks = split_text(resume_text)
        index, embeddings, chunks = create_vector_store(chunks)
        query = "Analyze this resume for weaknesses and suggestions"
        relevant_chunks = retrieve_chunks(query, index, chunks)
        context = "\n\n".join(relevant_chunks)

        # ✅ Get response
        response = bot.get_response(context, job_role)

        # ✅ STEP 5 — Clean structured output
        if "error" in response:
            print("\n⚠️ Error:", response["error"])
        else:
            print("\n📊 MATCH SCORE:", response.get("match_score", "N/A"))

            print("\n✅ Strengths:")
            for s in response.get("strengths", []):
                print(" -", s)

            print("\n❌ Missing Skills:")
            for m in response.get("missing_skills", []):
                print(" -", m)

            print("\n⚠️ Weaknesses:")
            for w in response.get("weaknesses", []):
                print(" -", w)

            print("\n💡 Suggestions:")
            for sug in response.get("suggestions", []):
                print(" -", sug)

        print("\n" + "="*50 + "\n")


if __name__ == "__main__":
    run_resume_analyzer()
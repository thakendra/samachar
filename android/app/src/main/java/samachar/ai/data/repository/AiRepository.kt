package samachar.ai.data.repository

import com.google.firebase.Firebase
import com.google.firebase.firestore.FieldValue
import com.google.firebase.firestore.Query
import com.google.firebase.firestore.firestore
import kotlinx.coroutines.tasks.await
import samachar.ai.data.model.AiLogEntry

/**
 * Wraps the Samachar AI Flask backend (/api/ai/ask).
 * Falls back to a local rule table if the network call fails.
 */
class AiRepository {
    private val db = Firebase.firestore
    private val api = FlaskApiClient.service

    /**
     * Ask the AI. Returns (answer, sources).
     */
    suspend fun ask(question: String, language: String): Pair<String, List<String>> {
        return try {
            val resp = api.askAi(AiAskRequest(question = question, lang = language))
            if (resp.quotaExceeded) {
                "Your daily AI quota has been reached. Upgrade to Samachar Pro for unlimited queries." to emptyList()
            } else {
                resp.answer.trim() to resp.sources
            }
        } catch (e: kotlinx.coroutines.CancellationException) {
            throw e
        } catch (e: Exception) {
            fallback(question) to listOf("samachar.ai cache")
        }
    }

    private fun fallback(q: String): String {
        val lower = q.lowercase()
        return when {
            "budget" in lower -> "The Federal Budget 2081/82 commits Rs 1.75 trillion — Rs 180B for hydropower transmission, Rs 42B for the 7-city digital fibre corridor. Provinces share 50% of new cross-border electricity revenue."
            "nepse" in lower || "market" in lower -> "NEPSE closed at 2,184.6, up 2.3% on volume of Rs 6.2B. Banking subindex led with +3.8%. IMF Article IV flagged reserves at 11.3 months of imports."
            "gold" in lower -> "Gold is up on safe-haven flows + weaker NPR + wedding-season buying. Tola price around Rs 168,400 — up 2.1% week-on-week."
            "pulchowk" in lower || "road" in lower -> "Pulchowk footpath works started today. 3-month timeline. Traffic from Kupondole rerouted via Sanepa side roads 7-10 AM weekdays."
            "remit" in lower || "forex" in lower -> "Q1 formal Gulf remittances hit Rs 312B — up 11% YoY. Hawala spread narrowed to 0.4% from 1.2% a year ago."
            else -> "I don't have a confident answer right now. Try a more specific angle (timeline, fiscal numbers, ward-level impact) and I will dig deeper."
        }
    }

    suspend fun history(uid: String): List<AiLogEntry> =
        db.collection("users").document(uid).collection("ai_log")
            .orderBy("created_at", Query.Direction.DESCENDING).limit(50)
            .get().await().toObjects(AiLogEntry::class.java)

    suspend fun saveLog(uid: String, question: String, answer: String, sources: List<String>) {
        db.collection("users").document(uid).collection("ai_log").add(
            mapOf(
                "question" to question, "answer" to answer, "sources" to sources,
                "created_at" to System.currentTimeMillis(),
            )
        ).await()
    }

    suspend fun decrementQuota(uid: String) {
        db.collection("users").document(uid)
            .update("ai_quota", FieldValue.increment(-1)).await()
    }
}

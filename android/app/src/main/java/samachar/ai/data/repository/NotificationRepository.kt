package samachar.ai.data.repository

import com.google.firebase.Firebase
import com.google.firebase.firestore.Query
import com.google.firebase.firestore.firestore
import kotlinx.coroutines.tasks.await
import samachar.ai.data.model.Notification
import samachar.ai.data.model.Trend

class NotificationRepository {
    private val db = Firebase.firestore

    suspend fun list(): List<Notification> {
        return db.collection("notifications")
            .orderBy("created_at", Query.Direction.DESCENDING)
            .get().await().toObjects(Notification::class.java)
    }

    suspend fun readIds(uid: String): Set<String> =
        db.collection("users").document(uid).collection("notif_read")
            .get().await().documents.map { it.id }.toSet()

    suspend fun markRead(uid: String, nid: String) {
        db.collection("users").document(uid).collection("notif_read")
            .document(nid).set(mapOf("read_at" to System.currentTimeMillis())).await()
    }

    suspend fun markAllRead(uid: String) {
        val ids = list().map { it.id }
        val batch = db.batch()
        ids.forEach { nid ->
            val ref = db.collection("users").document(uid)
                .collection("notif_read").document(nid)
            batch.set(ref, mapOf("read_at" to System.currentTimeMillis()))
        }
        batch.commit().await()
    }

    suspend fun trends(): List<Trend> =
        db.collection("trends").orderBy("rank").get().await().toObjects(Trend::class.java)
}

package samachar.ai.data.repository

import com.google.firebase.Firebase
import com.google.firebase.firestore.FieldValue
import com.google.firebase.firestore.Query
import com.google.firebase.firestore.firestore
import kotlinx.coroutines.tasks.await
import samachar.ai.data.model.Comment

/**
 * Comments live under articles/{aid}/comments/{cid}.
 * Vote state per user is stored under .../comments/{cid}/reactions/{uid}.
 */
class CommentRepository {
    private val db = Firebase.firestore

    private fun col(aid: String) =
        db.collection("articles").document(aid).collection("comments")

    suspend fun list(aid: String): List<Comment> {
        val snap = col(aid).orderBy("created_at", Query.Direction.DESCENDING).get().await()
        return snap.toObjects(Comment::class.java)
    }

    suspend fun post(aid: String, uid: String, name: String, place: String, text: String): Comment {
        val initials = name.split(" ").mapNotNull { it.firstOrNull()?.uppercaseChar() }
            .take(2).joinToString("")
            .ifBlank { "YO" }
        val data = mutableMapOf<String, Any?>(
            "article_id" to aid, "user_id" to uid,
            "name" to name, "initials" to initials,
            "place" to place, "text" to text,
            "likes" to 0, "dislikes" to 0, "verified" to false,
            "created_at" to System.currentTimeMillis(),
        )
        val ref = col(aid).add(data).await()
        db.collection("articles").document(aid)
            .update("comments_count", FieldValue.increment(1)).await()
        val snap = ref.get().await()
        return snap.toObject(Comment::class.java)!!
    }

    /**
     * Vote: 1 = like, -1 = dislike, 0 = clear.
     * Tally is adjusted by delta to keep things idempotent.
     */
    suspend fun vote(aid: String, cid: String, uid: String, vote: Int): Comment? {
        val rxRef = col(aid).document(cid).collection("reactions").document(uid)
        val cmtRef = col(aid).document(cid)
        val existing = rxRef.get().await()
        val old = existing.getLong("vote")?.toInt() ?: 0
        if (vote == 0) rxRef.delete().await()
        else rxRef.set(mapOf("vote" to vote)).await()

        val likeDelta = (if (vote == 1) 1 else 0) - (if (old == 1) 1 else 0)
        val disDelta  = (if (vote == -1) 1 else 0) - (if (old == -1) 1 else 0)
        if (likeDelta != 0) cmtRef.update("likes", FieldValue.increment(likeDelta.toLong())).await()
        if (disDelta != 0)  cmtRef.update("dislikes", FieldValue.increment(disDelta.toLong())).await()
        return cmtRef.get().await().toObject(Comment::class.java)
    }

    suspend fun myVote(aid: String, cid: String, uid: String): Int =
        col(aid).document(cid).collection("reactions").document(uid)
            .get().await().getLong("vote")?.toInt() ?: 0
}

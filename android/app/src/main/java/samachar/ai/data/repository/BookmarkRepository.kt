package samachar.ai.data.repository

import com.google.firebase.Firebase
import com.google.firebase.firestore.FieldValue
import com.google.firebase.firestore.firestore
import kotlinx.coroutines.tasks.await
import samachar.ai.data.model.Article

/**
 * Bookmarks live under users/{uid}/bookmarks/{articleId}.
 * Each doc just stores a timestamp + a denormalised copy of essentials so the
 * Saved screen renders without a second query per item.
 */
class BookmarkRepository {
    private val db = Firebase.firestore

    private fun col(uid: String) =
        db.collection("users").document(uid).collection("bookmarks")

    suspend fun listIds(uid: String): Set<String> {
        val snap = col(uid).get().await()
        return snap.documents.map { it.id }.toSet()
    }

    suspend fun list(uid: String): List<Article> {
        val snap = col(uid).orderBy("saved_at",
            com.google.firebase.firestore.Query.Direction.DESCENDING).get().await()
        return snap.toObjects(Article::class.java)
    }

    suspend fun toggle(uid: String, article: Article): Boolean {
        val ref = col(uid).document(article.id)
        val exists = ref.get().await().exists()
        if (exists) {
            ref.delete().await()
            return false
        } else {
            // Store the whole article so the saved view works offline.
            val data = mutableMapOf<String, Any?>(
                "id" to article.id, "title" to article.title, "title_np" to article.titleNp,
                "category" to article.category, "tag" to article.tag,
                "source" to article.source, "dek" to article.dek,
                "icon" to article.icon, "img_label" to article.imgLabel,
                "bias" to article.bias, "verified" to article.verified,
                "verified_count" to article.verifiedCount,
                "comments_count" to article.commentsCount, "likes" to article.likes,
                "developing" to article.developing, "is_video" to article.isVideo,
                "body" to article.body, "key_points" to article.keyPoints,
                "why_matters" to article.whyMatters,
                "published_at" to article.publishedAt,
                "time_label" to article.timeLabel,
                "saved_at" to FieldValue.serverTimestamp(),
            )
            ref.set(data).await()
            return true
        }
    }
}

package samachar.ai.data.repository

import com.google.firebase.Firebase
import com.google.firebase.firestore.Query
import com.google.firebase.firestore.firestore
import kotlinx.coroutines.tasks.await
import samachar.ai.data.model.Article

class ArticleRepository {
    private val db = Firebase.firestore
    private val col get() = db.collection("articles")

    suspend fun list(tag: String? = null, limit: Long = 50): List<Article> {
        var q: Query = col.orderBy("published_at", Query.Direction.DESCENDING).limit(limit)
        if (!tag.isNullOrBlank() && tag != "foryou") q = q.whereEqualTo("tag", tag)
        val snap = q.get().await()
        return snap.toObjects(Article::class.java)
    }

    suspend fun search(query: String, limit: Long = 50): List<Article> {
        // Firestore has no native full-text, so we pull recent + filter client-side.
        val recent = col.orderBy("published_at", Query.Direction.DESCENDING)
            .limit(200).get().await().toObjects(Article::class.java)
        val needle = query.trim().lowercase()
        if (needle.isEmpty()) return recent.take(limit.toInt())
        return recent.filter {
            it.title.lowercase().contains(needle) ||
            it.dek.lowercase().contains(needle) ||
            it.category.lowercase().contains(needle) ||
            it.body.any { p -> p.lowercase().contains(needle) } ||
            it.keyPoints.any { p -> p.lowercase().contains(needle) }
        }.take(limit.toInt())
    }

    suspend fun get(id: String): Article? {
        val snap = col.document(id).get().await()
        return snap.toObject(Article::class.java)
    }

    suspend fun related(article: Article, limit: Long = 3): List<Article> {
        val snap = col.whereEqualTo("tag", article.tag).limit(limit + 1).get().await()
        return snap.toObjects(Article::class.java).filter { it.id != article.id }.take(limit.toInt())
    }
}

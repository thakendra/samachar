package samachar.ai.data.repository

import android.util.Log
import samachar.ai.data.model.Article

class ArticleRepository {
    private val api = FlaskApiClient.service

    suspend fun list(tag: String? = null, limit: Long = 60): List<Article> {
        return try {
            val raw = api.articles(tag = if (tag == "foryou") null else tag, limit = limit.toInt())
            Log.d("SAM", "list() got ${raw.size} articles from server")
            val mapped = raw.mapNotNull { fa ->
                try { fa.toArticle() } catch (e: Exception) {
                    Log.e("SAM", "toArticle() failed for ${fa.id}: ${e.message}")
                    null
                }
            }
            Log.d("SAM", "list() mapped to ${mapped.size} Article objects")
            mapped
        } catch (e: Exception) {
            Log.e("SAM", "list() FAILED: ${e.javaClass.simpleName}: ${e.message}")
            throw e
        }
    }

    suspend fun search(query: String, limit: Long = 60): List<Article> =
        api.articles(q = query.trim().takeIf { it.isNotEmpty() }, limit = limit.toInt())
            .map { it.toArticle() }

    suspend fun get(id: String): Article? =
        runCatching { api.article(id).toArticle() }.getOrNull()

    suspend fun related(article: Article, limit: Long = 3): List<Article> =
        runCatching {
            api.articles(tag = article.tag, limit = 10)
                .filter { it.id != article.id }
                .take(limit.toInt())
                .map { it.toArticle() }
        }.getOrDefault(emptyList())
}

// ── Mapper: FlaskArticle → Article ───────────────────────────────────────────

fun FlaskArticle.toArticle() = Article(
    id           = id.orEmpty(),
    category     = category.orEmpty(),
    tag          = tag.orEmpty(),
    source       = source.orEmpty(),
    title        = title.orEmpty(),
    dek          = dek.orEmpty(),
    imgUrl       = imgUrl,
    imgLabel     = sourceColor,
    bias         = bias,
    biasLabel    = biasLabel,
    body         = body?.mapNotNull { it } ?: emptyList(),
    keyPoints    = keyPoints?.mapNotNull { it } ?: emptyList(),
    whyMatters   = whyMatters,
    publishedAt  = publishedAt ?: 0L,
    timeLabel    = timeLabel.orEmpty(),
    commentsCount= commentsCount ?: 0,
    likes        = likes ?: 0,
    developing   = developing ?: false,
)

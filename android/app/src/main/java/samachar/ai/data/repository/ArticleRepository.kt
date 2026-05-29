package samachar.ai.data.repository

import samachar.ai.data.model.Article

class ArticleRepository {
    private val api = FlaskApiClient.service

    suspend fun list(tag: String? = null, limit: Long = 60): List<Article> =
        api.articles(tag = if (tag == "foryou") null else tag, limit = limit.toInt())
            .map { it.toArticle() }

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

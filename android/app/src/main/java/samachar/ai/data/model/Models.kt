package samachar.ai.data.model

import com.google.firebase.firestore.DocumentId
import com.google.firebase.firestore.PropertyName

data class Article(
    @DocumentId var id: String = "",
    var category: String = "",
    var tag: String = "",
    var source: String = "",
    var title: String = "",
    @get:PropertyName("title_np") @set:PropertyName("title_np") var titleNp: String? = null,
    var dek: String = "",
    var icon: String? = null,
    @get:PropertyName("img_label") @set:PropertyName("img_label") var imgLabel: String? = null,
    var bias: Int? = null,
    @get:PropertyName("bias_label") @set:PropertyName("bias_label") var biasLabel: String? = null,
    var verified: Boolean = false,
    @get:PropertyName("verified_count") @set:PropertyName("verified_count") var verifiedCount: Int = 0,
    @get:PropertyName("comments_count") @set:PropertyName("comments_count") var commentsCount: Int = 0,
    var likes: Int = 0,
    var developing: Boolean = false,
    @get:PropertyName("is_video") @set:PropertyName("is_video") var isVideo: Boolean = false,
    var body: List<String> = emptyList(),
    @get:PropertyName("key_points") @set:PropertyName("key_points") var keyPoints: List<String> = emptyList(),
    @get:PropertyName("why_matters") @set:PropertyName("why_matters") var whyMatters: String? = null,
    @get:PropertyName("published_at") @set:PropertyName("published_at") var publishedAt: Long = 0L,
    @get:PropertyName("time_label") @set:PropertyName("time_label") var timeLabel: String = "",
)

data class UserProfile(
    @DocumentId var uid: String = "",
    var name: String = "",
    var email: String = "",
    var ward: String = "Ward 5, Lalitpur",
    var language: String = "en",
    var theme: String = "light",
    var accent: String = "#C92A2A",
    var density: String = "comfortable",
    var plan: String = "free",
    @get:PropertyName("ai_quota") @set:PropertyName("ai_quota") var aiQuota: Int = 10,
    @get:PropertyName("ai_quota_date") @set:PropertyName("ai_quota_date") var aiQuotaDate: String = "",
    var topics: List<String> = listOf("t1", "t3"),
    var onboarded: Boolean = false,
    @get:PropertyName("created_at") @set:PropertyName("created_at") var createdAt: Long = 0L,
)

data class Comment(
    @DocumentId var id: String = "",
    @get:PropertyName("article_id") @set:PropertyName("article_id") var articleId: String = "",
    @get:PropertyName("user_id") @set:PropertyName("user_id") var userId: String = "",
    var name: String = "",
    var initials: String = "",
    var place: String = "",
    var text: String = "",
    var likes: Int = 0,
    var dislikes: Int = 0,
    var verified: Boolean = false,
    @get:PropertyName("created_at") @set:PropertyName("created_at") var createdAt: Long = 0L,
)

data class Notification(
    @DocumentId var id: String = "",
    var icon: String = "bell",
    var tone: String = "info",
    var title: String = "",
    var sub: String = "",
    @get:PropertyName("created_at") @set:PropertyName("created_at") var createdAt: Long = 0L,
)

data class Trend(
    @DocumentId var id: String = "",
    var rank: Int = 0,
    var title: String = "",
    var sub: String = "",
    var heat: String = "rising",
)

data class AiMessage(
    val role: String,           // "user" | "ai" | "system"
    val text: String,
    val sources: List<String> = emptyList(),
)

data class AiLogEntry(
    @DocumentId var id: String = "",
    var question: String = "",
    var answer: String = "",
    var sources: List<String> = emptyList(),
    @get:PropertyName("created_at") @set:PropertyName("created_at") var createdAt: Long = 0L,
)

data class Topic(val id: String, val name: String, val sub: String, val icon: String)

object Topics {
    val ALL = listOf(
        Topic("t1", "Politics", "Sansad · parties · policy", "building"),
        Topic("t2", "Business", "NEPSE · trade · macro", "chart"),
        Topic("t3", "Hyperlocal", "Your ward · municipality", "pin"),
        Topic("t4", "Tech", "Fintech · digital · startup", "sparkle"),
        Topic("t5", "Agriculture", "Farming · prices · climate", "plant"),
        Topic("t6", "Remittance", "Diaspora · forex · banking", "globe"),
        Topic("t7", "Health", "Public health · hospitals", "shield-check"),
        Topic("t8", "Climate", "Floods · glaciers · air", "mountain"),
    )
}

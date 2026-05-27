package samachar.ai.data.repository

import com.google.gson.annotations.SerializedName
import okhttp3.JavaNetCookieJar
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import retrofit2.http.*
import java.net.CookieManager
import java.net.CookiePolicy
import java.util.concurrent.TimeUnit

// ── Data classes matching Flask JSON responses ────────────────────────────────

data class FlaskArticle(
    val id: String = "",
    val title: String = "",
    val dek: String = "",
    val source: String = "",
    @SerializedName("source_url") val sourceUrl: String? = null,
    @SerializedName("source_color") val sourceColor: String = "#14171C",
    val category: String = "WORLD",
    val tag: String = "nepal",
    @SerializedName("img_url") val imgUrl: String? = null,
    val bias: Int = 50,
    @SerializedName("bias_label") val biasLabel: String = "Center",
    val body: List<String> = emptyList(),
    @SerializedName("key_points") val keyPoints: List<String> = emptyList(),
    @SerializedName("why_matters") val whyMatters: String? = null,
    @SerializedName("published_at") val publishedAt: Long = 0L,
    @SerializedName("time_label") val timeLabel: String = "",
    @SerializedName("comments_count") val commentsCount: Int = 0,
    val likes: Int = 0,
    val developing: Boolean = false,
    val related: List<FlaskArticle>? = null,
)

data class FlaskUser(
    val id: Int = 0,
    val name: String = "",
    val email: String? = null,
    val ward: String = "Ward 5, Lalitpur",
    val language: String = "en",
    val theme: String = "light",
    val accent: String = "#C92A2A",
    val plan: String = "free",
    @SerializedName("ai_quota") val aiQuota: Int = 10,
    val onboarded: Int = 0,
    val topics: List<String> = emptyList(),
)

data class FlaskAiResponse(
    val answer: String = "",
    val sources: List<String> = emptyList(),
    val related: List<Any> = emptyList(),
    @SerializedName("remaining_quota") val remainingQuota: Int = 0,
    @SerializedName("quota_exceeded") val quotaExceeded: Boolean = false,
)

data class FlaskTrend(
    val rank: Int = 0,
    val title: String = "",
    val sub: String = "",
    val heat: String = "rising",
)

data class LoginRequest(val email: String, val password: String)
data class SignupRequest(val name: String, val email: String, val password: String, val ward: String = "Ward 5, Lalitpur")
data class AiAskRequest(val question: String, val lang: String = "np")

// ── Retrofit service interface ────────────────────────────────────────────────

interface FlaskApiService {
    @GET("api/articles")
    suspend fun articles(
        @Query("tag") tag: String? = null,
        @Query("q") q: String? = null,
        @Query("limit") limit: Int = 60,
    ): List<FlaskArticle>

    @GET("api/articles/{id}")
    suspend fun article(@Path("id") id: String): FlaskArticle

    @GET("api/trends")
    suspend fun trends(): List<FlaskTrend>

    @GET("api/auth/me")
    suspend fun me(): FlaskUser?

    @POST("api/auth/login")
    suspend fun login(@Body body: LoginRequest): FlaskUser

    @POST("api/auth/signup")
    suspend fun signup(@Body body: SignupRequest): FlaskUser

    @POST("api/auth/logout")
    suspend fun logout(): Map<String, Boolean>

    @POST("api/ai/ask")
    suspend fun askAi(@Body body: AiAskRequest): FlaskAiResponse
}

// ── Singleton client ──────────────────────────────────────────────────────────

object FlaskApiClient {
    const val BASE_URL = "https://samachar-wg5rea.fly.dev/"

    private val cookieJar = JavaNetCookieJar(
        CookieManager().apply { setCookiePolicy(CookiePolicy.ACCEPT_ALL) }
    )

    private val okHttp = OkHttpClient.Builder()
        .cookieJar(cookieJar)
        .connectTimeout(20, TimeUnit.SECONDS)
        .readTimeout(30, TimeUnit.SECONDS)
        .addInterceptor(HttpLoggingInterceptor().apply {
            level = HttpLoggingInterceptor.Level.BASIC
        })
        .build()

    val service: FlaskApiService = Retrofit.Builder()
        .baseUrl(BASE_URL)
        .client(okHttp)
        .addConverterFactory(GsonConverterFactory.create())
        .build()
        .create(FlaskApiService::class.java)
}

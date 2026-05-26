package samachar.ai.data.repository

import com.google.firebase.Firebase
import com.google.firebase.auth.FirebaseAuth
import com.google.firebase.auth.auth
import com.google.firebase.firestore.firestore
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.tasks.await
import samachar.ai.data.model.UserProfile
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

/**
 * Firebase Auth + Firestore-backed profile. Email/password for demo;
 * Google sign-in is wired up at the activity layer.
 */
class AuthRepository {
    private val auth = Firebase.auth
    private val db = Firebase.firestore

    private val _currentUser = MutableStateFlow(auth.currentUser?.uid)
    val currentUserId: StateFlow<String?> = _currentUser.asStateFlow()

    init {
        auth.addAuthStateListener { _currentUser.value = it.currentUser?.uid }
    }

    suspend fun signUp(email: String, password: String, name: String, ward: String): UserProfile {
        val res = auth.createUserWithEmailAndPassword(email, password).await()
        val uid = res.user!!.uid
        val today = SimpleDateFormat("yyyy-MM-dd", Locale.US).format(Date())
        val profile = UserProfile(
            uid = uid, name = name, email = email, ward = ward,
            aiQuotaDate = today, createdAt = System.currentTimeMillis(),
        )
        db.collection("users").document(uid).set(profile).await()
        return profile
    }

    suspend fun signIn(email: String, password: String): UserProfile {
        val res = auth.signInWithEmailAndPassword(email, password).await()
        return loadProfile(res.user!!.uid)
    }

    suspend fun signInAnonymous(name: String, ward: String): UserProfile {
        val res = auth.signInAnonymously().await()
        val uid = res.user!!.uid
        val today = SimpleDateFormat("yyyy-MM-dd", Locale.US).format(Date())
        val profile = UserProfile(
            uid = uid, name = name, email = "", ward = ward,
            aiQuotaDate = today, createdAt = System.currentTimeMillis(),
        )
        db.collection("users").document(uid).set(profile).await()
        return profile
    }

    suspend fun loadProfile(uid: String): UserProfile {
        val snap = db.collection("users").document(uid).get().await()
        val profile = snap.toObject(UserProfile::class.java) ?: UserProfile(uid = uid)
        // Reset daily AI quota at midnight (server-relative is fine for demo).
        val today = SimpleDateFormat("yyyy-MM-dd", Locale.US).format(Date())
        if (profile.aiQuotaDate != today) {
            val newQuota = if (profile.plan == "pro") 999 else 10
            db.collection("users").document(uid).update(
                mapOf("ai_quota" to newQuota, "ai_quota_date" to today)
            ).await()
            profile.aiQuota = newQuota
            profile.aiQuotaDate = today
        }
        return profile
    }

    suspend fun updateProfile(uid: String, updates: Map<String, Any?>) {
        db.collection("users").document(uid).update(updates).await()
    }

    fun signOut() = auth.signOut()
}

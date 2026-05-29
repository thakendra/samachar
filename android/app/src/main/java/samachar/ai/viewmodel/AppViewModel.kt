package samachar.ai.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.google.firebase.Firebase
import com.google.firebase.auth.auth
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import samachar.ai.data.model.Article
import samachar.ai.data.model.Notification
import samachar.ai.data.model.UserProfile
import samachar.ai.data.repository.AiRepository
import samachar.ai.data.repository.ArticleRepository
import samachar.ai.data.repository.AuthRepository
import samachar.ai.data.repository.BookmarkRepository
import samachar.ai.data.repository.CommentRepository
import samachar.ai.data.repository.NotificationRepository

class AppViewModel : ViewModel() {

    val auth = AuthRepository()
    val articles = ArticleRepository()
    val bookmarks = BookmarkRepository()
    val comments = CommentRepository()
    val notifications = NotificationRepository()
    val ai = AiRepository()

    private val _user = MutableStateFlow<UserProfile?>(null)
    val user: StateFlow<UserProfile?> = _user.asStateFlow()

    private val _loading = MutableStateFlow(true)
    val loading: StateFlow<Boolean> = _loading.asStateFlow()

    private val _bookmarkIds = MutableStateFlow<Set<String>>(emptySet())
    val bookmarkIds: StateFlow<Set<String>> = _bookmarkIds.asStateFlow()

    private val _unreadNotifs = MutableStateFlow(0)
    val unreadNotifs: StateFlow<Int> = _unreadNotifs.asStateFlow()

    private val _allNotifs = MutableStateFlow<List<Notification>>(emptyList())
    val allNotifs: StateFlow<List<Notification>> = _allNotifs.asStateFlow()

    private val _readNotifs = MutableStateFlow<Set<String>>(emptySet())
    val readNotifs: StateFlow<Set<String>> = _readNotifs.asStateFlow()

    private val _toast = MutableStateFlow<String?>(null)
    val toast: StateFlow<String?> = _toast.asStateFlow()

    private val _currentArticle = MutableStateFlow<Article?>(null)
    val currentArticle: StateFlow<Article?> = _currentArticle.asStateFlow()

    private val _pendingAiQuestion = MutableStateFlow<String?>(null)
    val pendingAiQuestion: StateFlow<String?> = _pendingAiQuestion.asStateFlow()

    private val _searchQuery = MutableStateFlow("")
    val searchQuery: StateFlow<String> = _searchQuery.asStateFlow()

    init {
        // Bootstrap: if a Firebase session exists, hydrate the profile.
        val currentUid = Firebase.auth.currentUser?.uid
        if (currentUid != null) {
            viewModelScope.launch {
                try {
                    // 8 s timeout — Firestore can hang forever on cold emulator/no-net
                    kotlinx.coroutines.withTimeout(8_000L) {
                        _user.value = auth.loadProfile(currentUid)
                        refreshBookmarks()
                        refreshNotifications()
                    }
                } catch (e: kotlinx.coroutines.TimeoutCancellationException) {
                    // Timed out — proceed as guest; user can sign in manually
                    Firebase.auth.signOut()
                } catch (e: Exception) {
                    Firebase.auth.signOut()
                } finally {
                    _loading.value = false
                }
            }
        } else {
            _loading.value = false
        }
    }

    fun toast(msg: String) {
        _toast.value = msg
        viewModelScope.launch {
            kotlinx.coroutines.delay(2200)
            _toast.value = null
        }
    }

    fun setCurrentArticle(a: Article?) { _currentArticle.value = a }
    fun setSearchQuery(q: String) { _searchQuery.value = q }
    fun setPendingAi(q: String?) { _pendingAiQuestion.value = q }

    fun setUser(p: UserProfile?) {
        _user.value = p
        if (p != null) viewModelScope.launch {
            refreshBookmarks()
            refreshNotifications()
        }
    }

    suspend fun refreshUser() {
        val uid = _user.value?.uid ?: return
        _user.value = auth.loadProfile(uid)
    }

    suspend fun refreshBookmarks() {
        val uid = _user.value?.uid ?: return
        _bookmarkIds.value = bookmarks.listIds(uid)
    }

    suspend fun refreshNotifications() {
        val uid = _user.value?.uid ?: return
        val all = notifications.list()
        val read = notifications.readIds(uid)
        _allNotifs.value = all
        _readNotifs.value = read
        _unreadNotifs.value = (all.map { it.id }.toSet() - read).size
    }

    fun toggleBookmark(article: Article) {
        val uid = _user.value?.uid ?: return
        viewModelScope.launch {
            val saved = bookmarks.toggle(uid, article)
            val next = _bookmarkIds.value.toMutableSet()
            if (saved) next.add(article.id) else next.remove(article.id)
            _bookmarkIds.value = next
            toast(if (saved) "Saved" else "Removed")
        }
    }

    fun isBookmarked(id: String) = id in _bookmarkIds.value

    fun signOut() {
        auth.signOut()
        _user.value = null
        _bookmarkIds.value = emptySet()
        _unreadNotifs.value = 0
    }

    fun updatePref(key: String, value: Any?) {
        val uid = _user.value?.uid ?: return
        viewModelScope.launch {
            auth.updateProfile(uid, mapOf(key to value))
            refreshUser()
        }
    }
}

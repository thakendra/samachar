package samachar.ai.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.ArrowForward
import androidx.compose.material.icons.outlined.AutoAwesome
import androidx.compose.material.icons.outlined.PlayArrow
import androidx.compose.material.icons.outlined.Search
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Icon
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavController
import kotlinx.coroutines.launch
import samachar.ai.data.model.Article
import samachar.ai.ui.components.*
import samachar.ai.ui.navigation.Routes
import samachar.ai.ui.theme.SamacharTheme
import samachar.ai.ui.theme.SerifFamily
import samachar.ai.viewmodel.AppViewModel

@Composable
fun HomeScreen(vm: AppViewModel, nav: NavController) {
    val palette = SamacharTheme.palette
    val scope = rememberCoroutineScope()
    val user by vm.user.collectAsState()
    val unread by vm.unreadNotifs.collectAsState()
    val bookmarkIds by vm.bookmarkIds.collectAsState()

    var tab by remember { mutableStateOf("foryou") }
    var articles by remember { mutableStateOf<List<Article>?>(null) }
    var loading by remember { mutableStateOf(true) }

    LaunchedEffect(tab) {
        loading = true; articles = null
        try {
            articles = vm.articles.list(tag = tab)
        } catch (e: kotlinx.coroutines.CancellationException) {
            throw e  // tab switched — not an error, just re-throw
        } catch (e: Exception) {
            articles = emptyList()
            vm.toast("Could not load feed — check connection")
        }
        loading = false
    }

    Column(Modifier.fillMaxSize()) {
        TopBar(
            ward = user?.ward ?: "Ward 5, Lalitpur",
            unread = unread,
            onNotifClick = { nav.navigate(Routes.NOTIFICATIONS) },
            onProfileClick = { nav.navigate(Routes.PROFILE) },
        )
        SearchPlate { nav.navigate(Routes.SEARCH) }

        // Date masthead row
        Row(
            Modifier
                .fillMaxWidth()
                .border(width = 1.dp, color = palette.rule)
                .padding(start = 20.dp, end = 20.dp, top = 8.dp, bottom = 18.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            val date = java.text.SimpleDateFormat("EEEE · d MMM", java.util.Locale.US)
                .format(java.util.Date()).uppercase()
            Text(date, fontFamily = SerifFamily, fontWeight = FontWeight.Bold,
                fontSize = 13.sp, color = palette.ink1, letterSpacing = 0.5.sp)
            Spacer(Modifier.weight(1f))
            MetaText("${articles?.size ?: 0} STORIES", color = palette.ink3)
            Spacer(Modifier.width(10.dp))
            Dot(color = palette.accent)
            Spacer(Modifier.width(4.dp))
            MetaText("LIVE")
        }

        // Filter pills
        val filters = listOf("foryou" to "For You", "nepal" to "Nepal", "hyperlocal" to "Hyperlocal",
            "business" to "Business", "tech" to "Tech", "agri" to "Agri")
        Row(
            Modifier.horizontalScroll(rememberScrollState())
                .padding(horizontal = 20.dp, vertical = 14.dp),
            horizontalArrangement = Arrangement.spacedBy(6.dp),
        ) {
            filters.forEach { (id, label) -> Pill(label, tab == id) { tab = id } }
        }

        if (loading) {
            Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                CircularProgressIndicator(color = palette.ink1, strokeWidth = 2.dp,
                    modifier = Modifier.size(20.dp))
            }
            return
        }

        val list = articles.orEmpty()
        LazyColumn(Modifier.fillMaxSize()) {
            // Voice brief banner
            item { VoiceBriefBanner() }

            // Lead article
            list.firstOrNull()?.let { a ->
                item {
                    NewsCard(
                        article = a, bookmarked = a.id in bookmarkIds,
                        language = user?.language ?: "en", isLead = true,
                        onOpen = {
                            vm.setCurrentArticle(a); nav.navigate(Routes.ARTICLE)
                        },
                        onBookmark = { vm.toggleBookmark(a) },
                        onShare = { vm.toast("Share link copied") },
                    )
                }
            }

            // Flood alert strip (For You only)
            if (tab == "foryou") {
                item {
                    FloodWatch { nav.navigate(Routes.NOTIFICATIONS) }
                }
            }

            // Rest of articles
            items(list.drop(1)) { a ->
                NewsCard(
                    article = a, bookmarked = a.id in bookmarkIds,
                    language = user?.language ?: "en",
                    onOpen = {
                        vm.setCurrentArticle(a); nav.navigate(Routes.ARTICLE)
                    },
                    onBookmark = { vm.toggleBookmark(a) },
                    onShare = { vm.toast("Share link copied") },
                )
            }

            // Premium teaser for free users
            if (user?.plan == "free") {
                item {
                    PremiumTeaser { nav.navigate(Routes.PREMIUM) }
                }
            }

            // Empty state
            if (list.isEmpty()) {
                item {
                    Box(Modifier.fillMaxWidth().padding(60.dp), contentAlignment = Alignment.Center) {
                        Text("No stories for this filter.",
                            fontFamily = SerifFamily, fontSize = 16.sp, color = palette.ink2)
                    }
                }
            }
        }
    }
}

@Composable
private fun SearchPlate(onClick: () -> Unit) {
    val palette = SamacharTheme.palette
    Row(
        Modifier
            .fillMaxWidth()
            .padding(start = 20.dp, end = 20.dp, top = 4.dp, bottom = 16.dp)
            .clip(RoundedCornerShape(14.dp))
            .background(palette.bgElev)
            .border(1.dp, palette.rule, RoundedCornerShape(14.dp))
            .clickable(onClick = onClick)
            .padding(horizontal = 14.dp, vertical = 12.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Icon(Icons.Outlined.Search, null, tint = palette.ink3, modifier = Modifier.size(16.dp))
        Spacer(Modifier.width(10.dp))
        Text("Search · खोज्नुहोस् · Ask AI…",
            color = palette.ink3, fontSize = 13.sp, fontWeight = FontWeight.Medium,
            modifier = Modifier.weight(1f))
        Tag("Ask AI", bg = palette.infoSoft, fg = palette.info)
    }
}

@Composable
private fun VoiceBriefBanner() {
    val palette = SamacharTheme.palette
    var playing by remember { mutableStateOf(false) }
    Row(
        Modifier
            .fillMaxWidth()
            .padding(horizontal = 20.dp, vertical = 4.dp)
            .clip(RoundedCornerShape(14.dp))
            .background(palette.ink1)
            .padding(horizontal = 16.dp, vertical = 14.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Box(
            Modifier
                .size(42.dp)
                .clip(CircleShape)
                .background(palette.bgElev)
                .clickable { playing = !playing },
            contentAlignment = Alignment.Center,
        ) {
            Icon(Icons.Outlined.PlayArrow, null, tint = palette.ink1, modifier = Modifier.size(16.dp))
        }
        Spacer(Modifier.width(14.dp))
        Column(Modifier.weight(1f)) {
            Text("YOUR MORNING BRIEF", color = palette.bgElev.copy(alpha = 0.55f),
                fontSize = 10.sp, fontWeight = FontWeight.Medium, letterSpacing = 1.4.sp)
            Text("आजको मुख्य ५ कुरा · 5 min", color = palette.bgElev,
                fontFamily = SerifFamily, fontSize = 15.sp, fontWeight = FontWeight.SemiBold)
        }
        Tag("PRO", bg = palette.bgElev.copy(alpha = 0.1f), fg = palette.bgElev.copy(alpha = 0.7f))
    }
}

@Composable
private fun FloodWatch(onClick: () -> Unit) {
    val palette = SamacharTheme.palette
    Row(
        Modifier
            .fillMaxWidth()
            .padding(horizontal = 20.dp)
            .clip(RoundedCornerShape(10.dp))
            .background(palette.accentSoft)
            .border(width = 2.dp, color = palette.accent, shape = RoundedCornerShape(0.dp))
            .clickable(onClick = onClick)
            .padding(horizontal = 14.dp, vertical = 12.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Dot(color = palette.accent)
        Spacer(Modifier.width(12.dp))
        Column(Modifier.weight(1f)) {
            Text("Valley flood watch", color = palette.accent,
                fontSize = 12.5.sp, fontWeight = FontWeight.Bold)
            MetaText("Wards 5, 9, 12 · SMS alerts on", color = palette.ink2)
        }
        Icon(Icons.Outlined.ArrowForward, null, tint = palette.accent,
            modifier = Modifier.size(14.dp))
    }
}

@Composable
private fun PremiumTeaser(onClick: () -> Unit) {
    val palette = SamacharTheme.palette
    Column(
        Modifier
            .fillMaxWidth()
            .padding(horizontal = 20.dp, vertical = 14.dp)
            .clip(RoundedCornerShape(14.dp))
            .background(palette.bgElev)
            .border(1.dp, palette.ink1, RoundedCornerShape(14.dp))
            .clickable(onClick = onClick)
            .padding(18.dp),
    ) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            Icon(Icons.Outlined.AutoAwesome, null, tint = palette.ink1,
                modifier = Modifier.size(14.dp))
            Spacer(Modifier.width(8.dp))
            Eyebrow("SAMACHAR PRO", color = palette.ink1)
        }
        Spacer(Modifier.height(10.dp))
        Text("Unlimited AI chat — Rs 79/month.",
            fontFamily = SerifFamily, fontSize = 19.sp, fontWeight = FontWeight.SemiBold,
            color = palette.ink1, lineHeight = 22.sp)
        Spacer(Modifier.height(8.dp))
        Text(
            "Ask any question about Nepal news. Multi-source bias comparison across left, centre and right outlets.",
            fontSize = 12.5.sp, color = palette.ink2, lineHeight = 18.sp,
        )
    }
}

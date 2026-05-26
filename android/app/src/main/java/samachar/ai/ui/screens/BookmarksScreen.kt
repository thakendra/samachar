package samachar.ai.ui.screens

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.ArrowBack
import androidx.compose.material.icons.outlined.Bookmark
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Icon
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavController
import samachar.ai.data.model.Article
import samachar.ai.ui.components.MetaText
import samachar.ai.ui.components.NewsCard
import samachar.ai.ui.navigation.Routes
import samachar.ai.ui.theme.SamacharTheme
import samachar.ai.ui.theme.SerifFamily
import samachar.ai.viewmodel.AppViewModel

@Composable
fun BookmarksScreen(vm: AppViewModel, nav: NavController) {
    val palette = SamacharTheme.palette
    val user by vm.user.collectAsState()
    val bookmarkIds by vm.bookmarkIds.collectAsState()
    var items by remember { mutableStateOf<List<Article>?>(null) }

    LaunchedEffect(user?.uid, bookmarkIds.size) {
        val uid = user?.uid ?: return@LaunchedEffect
        items = vm.bookmarks.list(uid)
    }

    Column(Modifier.fillMaxSize()) {
        Row(Modifier.fillMaxWidth().padding(start = 8.dp, end = 20.dp, top = 8.dp, bottom = 8.dp),
            verticalAlignment = Alignment.CenterVertically) {
            Icon(Icons.Outlined.ArrowBack, null, tint = palette.ink1,
                modifier = Modifier.padding(12.dp).size(16.dp).clickable { nav.popBackStack() })
            Spacer(Modifier.weight(1f))
            Text("Saved", fontFamily = SerifFamily, fontWeight = FontWeight.Bold,
                fontSize = 18.sp, color = palette.ink1)
            Spacer(Modifier.weight(1f))
            Spacer(Modifier.width(60.dp))
        }
        when {
            items == null -> Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                CircularProgressIndicator(color = palette.ink1, strokeWidth = 2.dp, modifier = Modifier.size(20.dp))
            }
            items!!.isEmpty() -> Column(
                Modifier.fillMaxSize().padding(60.dp),
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.Center,
            ) {
                Icon(Icons.Outlined.Bookmark, null, tint = palette.ink4, modifier = Modifier.size(32.dp))
                Spacer(Modifier.height(14.dp))
                Text("No saved stories yet", fontFamily = SerifFamily, fontSize = 18.sp,
                    fontWeight = FontWeight.SemiBold, color = palette.ink1)
                Spacer(Modifier.height(8.dp))
                Text("Tap the bookmark icon on any article to save it.",
                    fontSize = 13.sp, color = palette.ink2, textAlign = TextAlign.Center)
            }
            else -> LazyColumn(Modifier.fillMaxSize()) {
                item {
                    MetaText("${items!!.size} SAVED",
                        modifier = Modifier.padding(horizontal = 20.dp, vertical = 12.dp))
                }
                items(items!!) { a ->
                    NewsCard(
                        article = a, bookmarked = a.id in bookmarkIds,
                        language = user?.language ?: "en",
                        onOpen = { vm.setCurrentArticle(a); nav.navigate(Routes.ARTICLE) },
                        onBookmark = { vm.toggleBookmark(a) },
                        onShare = { vm.toast("Link copied") },
                    )
                }
            }
        }
    }
}

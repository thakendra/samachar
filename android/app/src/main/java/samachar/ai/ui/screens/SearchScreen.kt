package samachar.ai.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.ArrowBack
import androidx.compose.material.icons.outlined.AutoAwesome
import androidx.compose.material.icons.outlined.Close
import androidx.compose.material.icons.outlined.Search
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.OutlinedTextFieldDefaults
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.focus.FocusRequester
import androidx.compose.ui.focus.focusRequester
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavController
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import samachar.ai.data.model.Article
import samachar.ai.ui.components.MetaText
import samachar.ai.ui.components.NewsCard
import samachar.ai.ui.navigation.Routes
import samachar.ai.ui.theme.SamacharTheme
import samachar.ai.ui.theme.SerifFamily
import samachar.ai.viewmodel.AppViewModel

@Composable
fun SearchScreen(vm: AppViewModel, nav: NavController) {
    val palette = SamacharTheme.palette
    val scope = rememberCoroutineScope()
    val initialQ by vm.searchQuery.collectAsState()
    val user by vm.user.collectAsState()
    val bookmarkIds by vm.bookmarkIds.collectAsState()
    var q by remember { mutableStateOf(initialQ) }
    var results by remember { mutableStateOf<List<Article>>(emptyList()) }
    var busy by remember { mutableStateOf(false) }
    val focus = remember { FocusRequester() }

    LaunchedEffect(Unit) { focus.requestFocus() }

    LaunchedEffect(q) {
        delay(220)
        busy = true
        try {
            results = if (q.isBlank()) vm.articles.list() else vm.articles.search(q)
        } catch (_: Exception) {} finally { busy = false }
    }

    Column(Modifier.fillMaxSize()) {
        Row(
            Modifier.fillMaxWidth().padding(start = 8.dp, end = 20.dp, top = 8.dp, bottom = 8.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Icon(Icons.Outlined.ArrowBack, null, tint = palette.ink1,
                modifier = Modifier.padding(12.dp).size(16.dp).clickable { nav.popBackStack() })
            Row(
                Modifier.weight(1f).clip(RoundedCornerShape(12.dp))
                    .background(palette.bgElev)
                    .border(1.dp, palette.rule, RoundedCornerShape(12.dp))
                    .padding(horizontal = 14.dp),
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Icon(Icons.Outlined.Search, null, tint = palette.ink3, modifier = Modifier.size(14.dp))
                Spacer(Modifier.width(10.dp))
                OutlinedTextField(
                    value = q, onValueChange = { q = it },
                    placeholder = { Text("Search articles…", fontSize = 13.sp) },
                    singleLine = true,
                    colors = OutlinedTextFieldDefaults.colors(
                        focusedBorderColor = Color.Transparent, unfocusedBorderColor = Color.Transparent,
                        focusedContainerColor = Color.Transparent, unfocusedContainerColor = Color.Transparent,
                    ),
                    modifier = Modifier.weight(1f).focusRequester(focus),
                )
                if (q.isNotBlank()) {
                    Icon(Icons.Outlined.Close, null, tint = palette.ink3,
                        modifier = Modifier.size(14.dp).clickable { q = "" })
                }
            }
        }
        MetaText(
            if (busy) "SEARCHING…"
            else "${results.size} RESULT${if (results.size == 1) "" else "S"}" + (if (q.isNotBlank()) " · \"$q\"" else ""),
            color = palette.ink3,
            modifier = Modifier.padding(horizontal = 20.dp, vertical = 12.dp),
        )
        if (!busy && results.isEmpty() && q.isNotBlank()) {
            Column(
                Modifier.fillMaxSize().padding(30.dp),
                horizontalAlignment = Alignment.CenterHorizontally,
            ) {
                Text("No matches.", fontFamily = SerifFamily, fontSize = 16.sp,
                    fontWeight = FontWeight.SemiBold, color = palette.ink2)
                Spacer(Modifier.height(14.dp))
                Button(
                    onClick = { vm.setPendingAi(q); nav.navigate(Routes.AI) },
                    colors = ButtonDefaults.buttonColors(containerColor = palette.ink1, contentColor = palette.bgElev),
                    shape = RoundedCornerShape(50),
                ) {
                    Icon(Icons.Outlined.AutoAwesome, null, modifier = Modifier.size(14.dp))
                    Spacer(Modifier.width(6.dp))
                    Text("Ask AI: \"$q\"", fontWeight = FontWeight.SemiBold, fontSize = 13.sp)
                }
            }
        } else {
            LazyColumn {
                items(results) { a ->
                    NewsCard(
                        article = a, bookmarked = a.id in bookmarkIds,
                        language = user?.language ?: "en",
                        onOpen = { vm.setCurrentArticle(a); nav.navigate(Routes.ARTICLE) },
                        onBookmark = { vm.toggleBookmark(a) },
                        onShare = { vm.toast("Share copied") },
                    )
                }
            }
        }
    }
}

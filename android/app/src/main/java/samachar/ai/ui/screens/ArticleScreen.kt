package samachar.ai.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.ArrowBack
import androidx.compose.material.icons.outlined.AutoAwesome
import androidx.compose.material.icons.outlined.Bookmark
import androidx.compose.material.icons.outlined.Send
import androidx.compose.material.icons.outlined.Share
import androidx.compose.material.icons.outlined.ThumbDown
import androidx.compose.material.icons.outlined.ThumbUp
import androidx.compose.material.icons.outlined.VerifiedUser
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Icon
import androidx.compose.material3.OutlinedTextField
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
import samachar.ai.data.model.Comment
import samachar.ai.ui.components.*
import samachar.ai.ui.navigation.Routes
import samachar.ai.ui.theme.MonoFamily
import samachar.ai.ui.theme.SamacharTheme
import samachar.ai.ui.theme.SerifFamily
import samachar.ai.viewmodel.AppViewModel

@Composable
fun ArticleScreen(vm: AppViewModel, nav: NavController) {
    val palette = SamacharTheme.palette
    val scope = rememberCoroutineScope()
    val user by vm.user.collectAsState()
    val a by vm.currentArticle.collectAsState()
    val bookmarkIds by vm.bookmarkIds.collectAsState()

    var comments by remember { mutableStateOf<List<Comment>>(emptyList()) }
    var reply by remember { mutableStateOf("") }
    var votes by remember { mutableStateOf<Map<String, Int>>(emptyMap()) }
    var related by remember { mutableStateOf<List<samachar.ai.data.model.Article>>(emptyList()) }

    LaunchedEffect(a?.id, user?.uid) {
        val art = a ?: return@LaunchedEffect
        val uid = user?.uid ?: return@LaunchedEffect
        comments = vm.comments.list(art.id)
        related = vm.articles.related(art)
        // Load vote state per comment for this user
        val m = mutableMapOf<String, Int>()
        comments.forEach { m[it.id] = vm.comments.myVote(art.id, it.id, uid) }
        votes = m
    }

    if (a == null) {
        Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
            CircularProgressIndicator(color = palette.ink1, strokeWidth = 2.dp,
                modifier = Modifier.size(20.dp))
        }
        return
    }
    val article = a!!
    val isBm = article.id in bookmarkIds
    val title = if (user?.language == "np" && !article.titleNp.isNullOrBlank()) article.titleNp!! else article.title

    fun submitComment() {
        val text = reply.trim()
        val uid = user?.uid ?: return
        if (text.isEmpty()) return
        scope.launch {
            try {
                val c = vm.comments.post(article.id, uid, user!!.name, user!!.ward, text)
                comments = listOf(c) + comments
                reply = ""
                vm.toast("Comment posted")
            } catch (e: Exception) { vm.toast(e.message ?: "Post failed") }
        }
    }

    fun vote(cid: String, v: Int) {
        val uid = user?.uid ?: return
        val cur = votes[cid] ?: 0
        val applied = if (cur == v) 0 else v
        scope.launch {
            try {
                val updated = vm.comments.vote(article.id, cid, uid, applied)
                if (updated != null) {
                    comments = comments.map { if (it.id == cid) updated else it }
                }
                votes = votes + (cid to applied)
            } catch (e: Exception) { vm.toast(e.message ?: "Vote failed") }
        }
    }

    LazyColumn(Modifier.fillMaxSize()) {
        // Header
        item {
            Row(
                Modifier.fillMaxWidth().padding(start = 20.dp, end = 20.dp, top = 8.dp, bottom = 14.dp),
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Row(verticalAlignment = Alignment.CenterVertically,
                    modifier = Modifier.clickable { nav.popBackStack() }) {
                    Icon(Icons.Outlined.ArrowBack, null, tint = palette.ink1,
                        modifier = Modifier.size(16.dp))
                    Spacer(Modifier.width(6.dp))
                    Text("Back", fontSize = 12.5.sp, fontWeight = FontWeight.SemiBold,
                        color = palette.ink1)
                }
                Spacer(Modifier.weight(1f))
                IconButton34(Icons.Outlined.Bookmark, { vm.toggleBookmark(article) },
                    color = if (isBm) palette.accent else palette.ink1)
                Spacer(Modifier.width(6.dp))
                IconButton34(Icons.Outlined.Share, { vm.toast("Share link copied") })
            }
        }

        // Title + dek + byline
        item {
            Column(Modifier.padding(horizontal = 20.dp, vertical = 8.dp)) {
                Eyebrow(article.category, color = palette.ink3)
                Spacer(Modifier.height(14.dp))
                Text(title, fontFamily = SerifFamily, fontWeight = FontWeight.SemiBold,
                    fontSize = 28.sp, color = palette.ink1, lineHeight = 32.sp)
                Spacer(Modifier.height(14.dp))
                Text(article.dek, fontSize = 16.sp, color = palette.ink2,
                    lineHeight = 24.sp, fontWeight = FontWeight.Normal)
                Spacer(Modifier.height(18.dp))
                Row(
                    Modifier.fillMaxWidth().border(1.dp, palette.rule)
                        .padding(vertical = 14.dp),
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    Box(
                        Modifier.size(32.dp).clip(CircleShape).background(palette.bgSunk),
                        contentAlignment = Alignment.Center,
                    ) {
                        Text(
                            article.source.split(" ").mapNotNull { it.firstOrNull() }
                                .take(2).joinToString("").uppercase(),
                            fontFamily = SerifFamily, fontWeight = FontWeight.Bold,
                            fontSize = 12.sp, color = palette.ink1,
                        )
                    }
                    Spacer(Modifier.width(10.dp))
                    Column(Modifier.weight(1f)) {
                        Text(article.source, fontSize = 12.5.sp, fontWeight = FontWeight.SemiBold,
                            color = palette.ink1)
                        MetaText("${article.category} · ${article.timeLabel}")
                    }
                    if (article.verified) Tag("VERIFIED",
                        bg = palette.verifySoft, fg = palette.verify)
                }
            }
        }

        // Hero placeholder
        item {
            Box(
                Modifier.fillMaxWidth().height(200.dp).background(palette.bgSunk),
                contentAlignment = Alignment.BottomStart,
            ) {
                MetaText(article.imgLabel ?: "PHOTOGRAPHY",
                    color = palette.ink3,
                    modifier = Modifier.padding(12.dp))
            }
        }

        // AI brief
        if (article.keyPoints.isNotEmpty()) {
            item { AiBriefBlock(article.keyPoints, user?.aiQuota ?: 10) }
        }

        // Why it matters
        if (!article.whyMatters.isNullOrBlank()) {
            item { WhyMatters(article.whyMatters!!) }
        }

        // Body
        items(article.body.withIndex().toList()) { (i, p) ->
            Text(
                p, fontFamily = SerifFamily, fontSize = 16.sp,
                color = palette.ink1, lineHeight = 26.sp,
                modifier = Modifier.padding(horizontal = 20.dp, vertical = 9.dp),
            )
        }

        // Action row
        item {
            Row(
                Modifier.fillMaxWidth().padding(horizontal = 20.dp, vertical = 20.dp),
                horizontalArrangement = Arrangement.spacedBy(8.dp),
            ) {
                ActionButton("Save", Icons.Outlined.Bookmark, weight = 1f) { vm.toggleBookmark(article) }
                ActionButton("Share", Icons.Outlined.Share, weight = 1f) { vm.toast("Link copied") }
                ActionButton("Ask AI", Icons.Outlined.AutoAwesome, weight = 1f, primary = true) {
                    vm.setPendingAi("Tell me more about: ${article.title.take(80)}")
                    nav.navigate(Routes.AI)
                }
            }
        }

        // Comments header
        item { SectionHeader("COMMENTS · ${comments.size}") }

        // Comment composer
        item {
            Row(
                Modifier.fillMaxWidth().padding(horizontal = 20.dp, vertical = 8.dp)
                    .clip(RoundedCornerShape(12.dp))
                    .background(palette.bgElev)
                    .border(1.dp, palette.rule, RoundedCornerShape(12.dp))
                    .padding(horizontal = 14.dp, vertical = 4.dp),
                verticalAlignment = Alignment.CenterVertically,
            ) {
                OutlinedTextField(
                    value = reply, onValueChange = { reply = it },
                    placeholder = { Text("Share your thoughts…", fontSize = 13.sp) },
                    singleLine = true,
                    modifier = Modifier.weight(1f),
                )
                Spacer(Modifier.width(6.dp))
                Icon(Icons.Outlined.Send, null,
                    tint = if (reply.isNotBlank()) palette.ink1 else palette.ink4,
                    modifier = Modifier.size(18.dp).clickable { submitComment() })
            }
        }

        // Comments list
        if (comments.isEmpty()) {
            item {
                Text("Be the first to comment.",
                    fontFamily = SerifFamily, fontStyle = androidx.compose.ui.text.font.FontStyle.Italic,
                    fontSize = 14.sp, color = palette.ink3,
                    modifier = Modifier.fillMaxWidth().padding(20.dp),
                    textAlign = androidx.compose.ui.text.style.TextAlign.Center)
            }
        }
        items(comments) { c ->
            CommentRow(c, votes[c.id] ?: 0, onVote = { v -> vote(c.id, v) })
        }

        // Related
        if (related.isNotEmpty()) {
            item { SectionHeader("MORE ON THIS STORY") }
            items(related) { r ->
                NewsCard(
                    article = r, bookmarked = r.id in bookmarkIds,
                    language = user?.language ?: "en",
                    onOpen = { vm.setCurrentArticle(r) },
                    onBookmark = { vm.toggleBookmark(r) },
                    onShare = { vm.toast("Link copied") },
                )
            }
        }
        item { Spacer(Modifier.height(40.dp)) }
    }
}

@Composable
private fun AiBriefBlock(points: List<String>, quota: Int) {
    val palette = SamacharTheme.palette
    Column(
        Modifier.fillMaxWidth()
            .padding(horizontal = 20.dp, vertical = 20.dp)
            .border(width = 1.dp, color = palette.ink1)
            .padding(vertical = 20.dp, horizontal = 0.dp),
    ) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            Icon(Icons.Outlined.AutoAwesome, null, tint = palette.ink1,
                modifier = Modifier.size(14.dp))
            Spacer(Modifier.width(6.dp))
            Eyebrow("AI BRIEF · 30 SECONDS", color = palette.ink1)
            Spacer(Modifier.weight(1f))
            MetaText("$quota/10", color = palette.ink3)
        }
        Spacer(Modifier.height(8.dp))
        points.forEachIndexed { i, p ->
            Row(verticalAlignment = Alignment.Top, modifier = Modifier.padding(vertical = 7.dp)) {
                Text(
                    "%02d".format(i + 1),
                    fontFamily = MonoFamily, fontSize = 11.sp,
                    color = palette.ink3, modifier = Modifier.padding(end = 14.dp),
                )
                Text(p, fontSize = 13.5.sp, color = palette.ink2, lineHeight = 20.sp)
            }
        }
    }
}

@Composable
private fun WhyMatters(text: String) {
    val palette = SamacharTheme.palette
    Column(
        Modifier.fillMaxWidth()
            .padding(horizontal = 20.dp, vertical = 12.dp)
            .clip(RoundedCornerShape(12.dp))
            .background(palette.bgElev)
            .border(1.dp, palette.rule, RoundedCornerShape(12.dp))
            .padding(16.dp),
    ) {
        Eyebrow("WHY THIS MATTERS · TO YOU", color = palette.verify)
        Spacer(Modifier.height(8.dp))
        Text(text, fontFamily = SerifFamily, fontSize = 14.sp,
            color = palette.ink1, lineHeight = 22.sp)
    }
}

@Composable
private fun ActionButton(
    label: String,
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    weight: Float,
    primary: Boolean = false,
    onClick: () -> Unit,
) {
    val palette = SamacharTheme.palette
    Row(
        Modifier
            .fillMaxWidth(weight)
            .clip(RoundedCornerShape(50))
            .background(if (primary) palette.ink1 else palette.bgElev)
            .border(1.dp, if (primary) palette.ink1 else palette.rule, RoundedCornerShape(50))
            .clickable(onClick = onClick)
            .padding(horizontal = 16.dp, vertical = 12.dp),
        horizontalArrangement = Arrangement.Center,
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Icon(icon, null, tint = if (primary) palette.bgElev else palette.ink1,
            modifier = Modifier.size(14.dp))
        Spacer(Modifier.width(6.dp))
        Text(label, color = if (primary) palette.bgElev else palette.ink1,
            fontSize = 13.sp, fontWeight = FontWeight.SemiBold)
    }
}

@Composable
private fun CommentRow(c: Comment, myVote: Int, onVote: (Int) -> Unit) {
    val palette = SamacharTheme.palette
    Column(Modifier.fillMaxWidth().padding(horizontal = 20.dp, vertical = 14.dp)) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            Box(
                Modifier.size(28.dp).clip(CircleShape).background(palette.bgSunk),
                contentAlignment = Alignment.Center,
            ) {
                Text(c.initials, fontFamily = SerifFamily, fontWeight = FontWeight.Bold,
                    fontSize = 11.sp, color = palette.ink1)
            }
            Spacer(Modifier.width(10.dp))
            Column(Modifier.weight(1f)) {
                Text(c.name, fontSize = 12.5.sp, fontWeight = FontWeight.SemiBold,
                    color = palette.ink1)
                MetaText("${c.place}")
            }
            if (c.verified) Icon(Icons.Outlined.VerifiedUser, null,
                tint = palette.verify, modifier = Modifier.size(14.dp))
        }
        Spacer(Modifier.height(8.dp))
        Text(c.text, fontFamily = SerifFamily, fontSize = 14.sp,
            color = palette.ink1, lineHeight = 21.sp)
        Spacer(Modifier.height(8.dp))
        Row(verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(14.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically,
                modifier = Modifier.clickable { onVote(1) }) {
                Icon(Icons.Outlined.ThumbUp, null,
                    tint = if (myVote == 1) palette.verify else palette.ink2,
                    modifier = Modifier.size(13.dp))
                Spacer(Modifier.width(5.dp))
                Text("${c.likes}", fontSize = 11.5.sp, color = palette.ink2)
            }
            Row(verticalAlignment = Alignment.CenterVertically,
                modifier = Modifier.clickable { onVote(-1) }) {
                Icon(Icons.Outlined.ThumbDown, null,
                    tint = if (myVote == -1) palette.accent else palette.ink3,
                    modifier = Modifier.size(13.dp))
                Spacer(Modifier.width(5.dp))
                Text("${c.dislikes}", fontSize = 11.5.sp, color = palette.ink3)
            }
        }
        Spacer(Modifier.height(14.dp))
        Rule()
    }
}

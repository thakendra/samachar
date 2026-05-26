package samachar.ai.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.ArrowBack
import androidx.compose.material.icons.outlined.ArrowForward
import androidx.compose.material.icons.outlined.AutoAwesome
import androidx.compose.material.icons.outlined.Send
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Icon
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.OutlinedTextFieldDefaults
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavController
import kotlinx.coroutines.launch
import samachar.ai.data.model.AiMessage
import samachar.ai.ui.components.Eyebrow
import samachar.ai.ui.components.MetaText
import samachar.ai.ui.theme.MonoFamily
import samachar.ai.ui.theme.SamacharTheme
import samachar.ai.ui.theme.SerifFamily
import samachar.ai.viewmodel.AppViewModel

private val SUGGESTIONS = listOf(
    "Why is gold price rising in Nepal?",
    "Summarise the federal budget",
    "NEPSE banking rally — what happened?",
    "How does the new wallet rule change Khalti?",
    "When is the U-19 semi vs India?",
)

@Composable
fun AiChatScreen(vm: AppViewModel, nav: NavController) {
    val palette = SamacharTheme.palette
    val scope = rememberCoroutineScope()
    val user by vm.user.collectAsState()
    val pending by vm.pendingAiQuestion.collectAsState()
    var messages by remember { mutableStateOf<List<AiMessage>>(emptyList()) }
    var input by remember { mutableStateOf("") }
    var typing by remember { mutableStateOf(false) }
    val listState = rememberLazyListState()
    var seedConsumed by remember { mutableStateOf(false) }

    fun send(text: String) {
        val q = text.trim()
        if (q.isEmpty() || user == null) return
        val plan = user!!.plan
        if (plan != "pro" && (user!!.aiQuota <= 0)) {
            messages = messages + AiMessage("user", q) +
                AiMessage("system", "Daily AI quota used. Upgrade to Pro for unlimited.")
            input = ""
            return
        }
        messages = messages + AiMessage("user", q)
        input = ""
        typing = true
        scope.launch {
            try {
                val (answer, sources) = vm.ai.ask(q, user!!.language)
                messages = messages + AiMessage("ai", answer, sources)
                if (plan != "pro") {
                    vm.ai.decrementQuota(user!!.uid)
                    vm.refreshUser()
                }
                vm.ai.saveLog(user!!.uid, q, answer, sources)
            } catch (e: Exception) {
                messages = messages + AiMessage("system", "Error: ${e.message?.take(80)}")
            } finally { typing = false }
        }
    }

    // Consume any pending question (e.g. from Discover or Article "Ask AI")
    LaunchedEffect(pending, user) {
        if (!seedConsumed && pending != null && user != null) {
            seedConsumed = true
            val q = pending!!
            vm.setPendingAi(null)
            send(q)
        }
    }

    LaunchedEffect(messages.size, typing) {
        val target = (messages.size + (if (typing) 1 else 0)) - 1
        if (target >= 0) listState.animateScrollToItem(target)
    }

    Column(Modifier.fillMaxSize()) {
        Row(
            Modifier.fillMaxWidth().padding(start = 8.dp, end = 20.dp, top = 8.dp, bottom = 8.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Icon(Icons.Outlined.ArrowBack, null, tint = palette.ink1,
                modifier = Modifier.padding(12.dp).size(16.dp).clickable { nav.popBackStack() })
            Spacer(Modifier.weight(1f))
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(Icons.Outlined.AutoAwesome, null, tint = palette.ink1, modifier = Modifier.size(14.dp))
                Spacer(Modifier.width(6.dp))
                Text("AI", fontFamily = SerifFamily, fontWeight = FontWeight.Bold,
                    fontSize = 17.sp, color = palette.ink1)
            }
            Spacer(Modifier.weight(1f))
            MetaText(if (user?.plan == "pro") "∞" else "${user?.aiQuota ?: 0}/10",
                color = palette.ink3)
        }

        LazyColumn(state = listState, modifier = Modifier.weight(1f).padding(horizontal = 16.dp)) {
            if (messages.isEmpty()) {
                item {
                    Column(Modifier.padding(vertical = 20.dp)) {
                        Eyebrow("SUGGESTIONS")
                        Spacer(Modifier.height(10.dp))
                        SUGGESTIONS.forEach { s ->
                            Row(
                                Modifier.fillMaxWidth().padding(vertical = 4.dp)
                                    .clip(RoundedCornerShape(12.dp))
                                    .background(palette.bgElev)
                                    .border(1.dp, palette.rule, RoundedCornerShape(12.dp))
                                    .clickable { send(s) }
                                    .padding(horizontal = 14.dp, vertical = 12.dp),
                                verticalAlignment = Alignment.CenterVertically,
                            ) {
                                Text(s, fontFamily = SerifFamily, fontSize = 13.5.sp,
                                    color = palette.ink1, modifier = Modifier.weight(1f))
                                Icon(Icons.Outlined.ArrowForward, null, tint = palette.ink3,
                                    modifier = Modifier.size(14.dp))
                            }
                        }
                    }
                }
            }
            items(messages) { m -> MessageBubble(m) }
            if (typing) {
                item {
                    Row(Modifier.fillMaxWidth().padding(vertical = 6.dp)) {
                        Box(
                            Modifier.clip(RoundedCornerShape(14.dp))
                                .background(palette.bgElev)
                                .border(1.dp, palette.rule, RoundedCornerShape(14.dp))
                                .padding(14.dp),
                        ) {
                            CircularProgressIndicator(color = palette.ink1, strokeWidth = 2.dp,
                                modifier = Modifier.size(16.dp))
                        }
                    }
                }
            }
        }

        // Composer
        Row(
            Modifier.fillMaxWidth().border(width = 1.dp, color = palette.rule)
                .padding(horizontal = 16.dp, vertical = 10.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            OutlinedTextField(
                value = input, onValueChange = { input = it },
                placeholder = { Text("Ask anything…", fontSize = 13.5.sp) },
                singleLine = true,
                modifier = Modifier.weight(1f),
                colors = OutlinedTextFieldDefaults.colors(
                    focusedBorderColor = palette.ink1, unfocusedBorderColor = palette.rule,
                ),
            )
            Spacer(Modifier.width(8.dp))
            Box(
                Modifier.size(44.dp).clip(RoundedCornerShape(50))
                    .background(if (input.isNotBlank() && !typing) palette.ink1 else palette.bgSunk)
                    .clickable(enabled = input.isNotBlank() && !typing) { send(input) },
                contentAlignment = Alignment.Center,
            ) {
                Icon(Icons.Outlined.Send, null,
                    tint = if (input.isNotBlank() && !typing) palette.bgElev else palette.ink3,
                    modifier = Modifier.size(16.dp))
            }
        }
    }
}

@Composable
private fun MessageBubble(m: AiMessage) {
    val palette = SamacharTheme.palette
    val isUser = m.role == "user"
    val isSystem = m.role == "system"
    Row(
        Modifier.fillMaxWidth().padding(vertical = 6.dp),
        horizontalArrangement = if (isUser) Arrangement.End else Arrangement.Start,
    ) {
        Box(
            Modifier
                .fillMaxWidth(0.85f)
                .clip(RoundedCornerShape(14.dp))
                .background(
                    when {
                        isUser -> palette.ink1
                        isSystem -> palette.accentSoft
                        else -> palette.bgElev
                    }
                )
                .border(
                    width = if (m.role == "ai") 1.dp else 0.dp,
                    color = if (m.role == "ai") palette.rule else Color.Transparent,
                    shape = RoundedCornerShape(14.dp),
                )
                .padding(14.dp),
        ) {
            Column {
                if (m.role == "ai") {
                    Eyebrow("AI · ${m.sources.size} SOURCES", color = palette.ink3)
                    Spacer(Modifier.height(6.dp))
                }
                Text(
                    m.text,
                    fontSize = 13.5.sp,
                    fontFamily = if (m.role == "ai") SerifFamily else null
                        ?: androidx.compose.ui.text.font.FontFamily.SansSerif,
                    color = when {
                        isUser -> palette.bgElev
                        isSystem -> palette.accent
                        else -> palette.ink1
                    },
                    lineHeight = 20.sp,
                )
                if (m.sources.isNotEmpty()) {
                    Spacer(Modifier.height(10.dp))
                    m.sources.forEach { s ->
                        MetaText("· $s", color = palette.ink3,
                            modifier = Modifier.padding(top = 2.dp))
                    }
                }
            }
        }
    }
}

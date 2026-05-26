package samachar.ai.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.ArrowForward
import androidx.compose.material.icons.outlined.Build
import androidx.compose.material.icons.outlined.LocationCity
import androidx.compose.material.icons.outlined.LocationOn
import androidx.compose.material.icons.outlined.MedicalServices
import androidx.compose.material.icons.outlined.QueryStats
import androidx.compose.material.icons.outlined.Spa
import androidx.compose.material.icons.outlined.Terrain
import androidx.compose.material.icons.outlined.Public
import androidx.compose.material.icons.outlined.AutoAwesome
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import kotlinx.coroutines.launch
import samachar.ai.data.model.Topics
import samachar.ai.ui.components.Eyebrow
import samachar.ai.ui.components.Pill
import samachar.ai.ui.theme.SamacharTheme
import samachar.ai.ui.theme.SerifFamily
import samachar.ai.viewmodel.AppViewModel

@Composable
fun OnboardingScreen(vm: AppViewModel, onDone: () -> Unit) {
    val palette = SamacharTheme.palette
    val scope = rememberCoroutineScope()
    val user by vm.user.collectAsState()
    var step by remember { mutableIntStateOf(0) }
    val selected = remember { mutableStateListOf("t1", "t3") }
    var lang by remember { mutableStateOf("en") }

    fun toggle(id: String) {
        if (id in selected) selected.remove(id) else selected.add(id)
    }

    fun finish() {
        val uid = user?.uid ?: return onDone()
        scope.launch {
            vm.auth.updateProfile(uid, mapOf(
                "topics" to selected.toList(),
                "language" to lang,
                "onboarded" to true,
            ))
            vm.refreshUser()
            onDone()
        }
    }

    Column(
        Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(horizontal = 24.dp, vertical = 20.dp)
    ) {
        // Progress bar
        Row(Modifier.padding(top = 28.dp, bottom = 36.dp), horizontalArrangement = Arrangement.spacedBy(6.dp)) {
            (0..2).forEach { i ->
                Box(
                    Modifier
                        .weight(if (i == step) 2f else 1f)
                        .height(3.dp)
                        .clip(RoundedCornerShape(2.dp))
                        .background(if (i <= step) palette.ink1 else palette.rule)
                )
            }
        }
        Eyebrow("Step ${step + 1} of 3")
        Spacer(Modifier.height(12.dp))

        when (step) {
            0 -> Step1Intro(onNext = { step = 1 }, onSkip = ::finish)
            1 -> Step2Topics(selected = selected, onToggle = ::toggle, onNext = { step = 2 })
            2 -> Step3Language(lang = lang, onLang = { lang = it }, onFinish = ::finish)
        }
    }
}

@Composable
private fun Step1Intro(onNext: () -> Unit, onSkip: () -> Unit) {
    val palette = SamacharTheme.palette
    Text(
        buildAnnotatedTitle("Nepal's news,", "understood", "."),
        fontFamily = SerifFamily, fontWeight = FontWeight.SemiBold, fontSize = 34.sp,
        color = palette.ink1, lineHeight = 38.sp,
    )
    Spacer(Modifier.height(14.dp))
    Text(
        "A reading layer over 50+ Nepali and English publishers — with AI summaries, source bias meters, and ward-level signal you can actually use.",
        fontSize = 14.sp, color = palette.ink2, lineHeight = 22.sp,
    )
    Spacer(Modifier.height(28.dp))
    Button(
        onClick = onNext,
        modifier = Modifier.fillMaxWidth().height(48.dp),
        shape = RoundedCornerShape(50),
        colors = ButtonDefaults.buttonColors(containerColor = palette.ink1, contentColor = palette.bgElev),
    ) {
        Text("Continue", fontWeight = FontWeight.SemiBold, fontSize = 14.sp)
        Spacer(Modifier.width(6.dp))
        Icon(Icons.Outlined.ArrowForward, null, modifier = Modifier.size(16.dp))
    }
    Spacer(Modifier.height(14.dp))
    Box(Modifier.fillMaxWidth(), contentAlignment = Alignment.Center) {
        TextButton(onClick = onSkip) {
            Text("Skip setup", fontSize = 12.sp, color = palette.ink3)
        }
    }
}

@Composable
private fun Step2Topics(selected: List<String>, onToggle: (String) -> Unit, onNext: () -> Unit) {
    val palette = SamacharTheme.palette
    val iconMap: Map<String, ImageVector> = mapOf(
        "building" to Icons.Outlined.LocationCity,
        "chart" to Icons.Outlined.QueryStats,
        "pin" to Icons.Outlined.LocationOn,
        "sparkle" to Icons.Outlined.AutoAwesome,
        "plant" to Icons.Outlined.Spa,
        "globe" to Icons.Outlined.Public,
        "shield-check" to Icons.Outlined.MedicalServices,
        "mountain" to Icons.Outlined.Terrain,
    )

    Text("Choose your beats", fontFamily = SerifFamily, fontWeight = FontWeight.SemiBold,
        fontSize = 28.sp, color = palette.ink1)
    Spacer(Modifier.height(10.dp))
    Text("Pick topics that should drive your feed. You can change this any time.",
        fontSize = 13.5.sp, color = palette.ink2)
    Spacer(Modifier.height(22.dp))

    val rows = Topics.ALL.chunked(2)
    rows.forEach { row ->
        Row(Modifier.fillMaxWidth().padding(bottom = 8.dp),
            horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            row.forEach { topic ->
                val on = topic.id in selected
                Column(
                    Modifier
                        .weight(1f)
                        .heightIn(min = 96.dp)
                        .clip(RoundedCornerShape(12.dp))
                        .background(if (on) palette.ink1 else palette.bgElev)
                        .border(1.dp, if (on) palette.ink1 else palette.rule, RoundedCornerShape(12.dp))
                        .clickable { onToggle(topic.id) }
                        .padding(14.dp),
                ) {
                    Icon(iconMap[topic.icon] ?: Icons.Outlined.Build, null,
                        tint = if (on) palette.bgElev else palette.ink1,
                        modifier = Modifier.size(20.dp))
                    Spacer(Modifier.weight(1f))
                    Text(topic.name, fontFamily = SerifFamily, fontWeight = FontWeight.SemiBold,
                        fontSize = 15.sp, color = if (on) palette.bgElev else palette.ink1)
                    Text(topic.sub, fontSize = 11.sp,
                        color = if (on) palette.bgElev.copy(alpha = 0.6f) else palette.ink3)
                }
            }
            if (row.size == 1) Box(Modifier.weight(1f))
        }
    }
    Spacer(Modifier.height(16.dp))
    Button(
        onClick = onNext, enabled = selected.isNotEmpty(),
        modifier = Modifier.fillMaxWidth().height(48.dp),
        shape = RoundedCornerShape(50),
        colors = ButtonDefaults.buttonColors(containerColor = palette.ink1, contentColor = palette.bgElev),
    ) {
        Text("Continue with ${selected.size} beats", fontWeight = FontWeight.SemiBold, fontSize = 14.sp)
        Spacer(Modifier.width(6.dp))
        Icon(Icons.Outlined.ArrowForward, null, modifier = Modifier.size(16.dp))
    }
}

@Composable
private fun Step3Language(lang: String, onLang: (String) -> Unit, onFinish: () -> Unit) {
    val palette = SamacharTheme.palette
    Text("Reading language", fontFamily = SerifFamily, fontWeight = FontWeight.SemiBold,
        fontSize = 28.sp, color = palette.ink1)
    Spacer(Modifier.height(10.dp))
    Text("Headlines will be translated. Body text stays in the original.",
        fontSize = 13.5.sp, color = palette.ink2)
    Spacer(Modifier.height(22.dp))
    Row(horizontalArrangement = Arrangement.spacedBy(6.dp), modifier = Modifier.fillMaxWidth()) {
        listOf("en" to "English", "np" to "नेपाली").forEach { (v, l) ->
            Box(Modifier.weight(1f)) { Pill(l, lang == v) { onLang(v) } }
        }
    }
    Spacer(Modifier.height(30.dp))
    Button(
        onClick = onFinish,
        modifier = Modifier.fillMaxWidth().height(48.dp),
        shape = RoundedCornerShape(50),
        colors = ButtonDefaults.buttonColors(containerColor = palette.ink1, contentColor = palette.bgElev),
    ) {
        Text("Open my front page", fontWeight = FontWeight.SemiBold, fontSize = 14.sp)
        Spacer(Modifier.width(6.dp))
        Icon(Icons.Outlined.ArrowForward, null, modifier = Modifier.size(16.dp))
    }
}

@Composable
private fun buildAnnotatedTitle(first: String, middle: String, accent: String) = buildString {
    append(first); append("\n"); append(middle); append(accent)
}

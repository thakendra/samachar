package samachar.ai.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import samachar.ai.ui.components.MetaText
import samachar.ai.ui.theme.SamacharTheme
import samachar.ai.ui.theme.SerifFamily

@Composable
fun SplashScreen() {
    val palette = SamacharTheme.palette
    Column(
        Modifier.fillMaxSize(),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        Text(
            "samachar.", fontFamily = SerifFamily, fontWeight = FontWeight.Bold,
            fontSize = 36.sp, color = palette.ink1,
        )
        MetaText("NEPAL'S NEWS, UNDERSTOOD", color = palette.ink3)
        Spacer(Modifier.height(40.dp))
        CircularProgressIndicator(color = palette.ink1, strokeWidth = 2.dp,
            modifier = Modifier.size(20.dp))
    }
}

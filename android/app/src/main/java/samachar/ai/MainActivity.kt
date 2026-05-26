package samachar.ai

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.activity.viewModels
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.Surface
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import samachar.ai.ui.navigation.AppNavGraph
import samachar.ai.ui.theme.SamacharTheme
import samachar.ai.viewmodel.AppViewModel

class MainActivity : ComponentActivity() {

    private val vm: AppViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            val user by vm.user.collectAsState()
            val themeMode = user?.theme ?: "light"
            SamacharTheme(dark = themeMode == "dark") {
                Surface(modifier = Modifier.fillMaxSize()) {
                    Box(modifier = Modifier
                        .fillMaxSize()
                        .background(SamacharTheme.palette.bg)) {
                        AppNavGraph(vm)
                    }
                }
            }
        }
    }
}

package samachar.ai.ui.navigation

import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Scaffold
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.compose.rememberNavController
import samachar.ai.ui.components.TabBar
import samachar.ai.ui.components.Toast
import samachar.ai.ui.screens.AiChatScreen
import samachar.ai.ui.screens.ArticleScreen
import samachar.ai.ui.screens.BookmarksScreen
import samachar.ai.ui.screens.DiscoverScreen
import samachar.ai.ui.screens.HomeScreen
import samachar.ai.ui.screens.LoginScreen
import samachar.ai.ui.screens.NotificationsScreen
import samachar.ai.ui.screens.OnboardingScreen
import samachar.ai.ui.screens.PremiumScreen
import samachar.ai.ui.screens.ProfileScreen
import samachar.ai.ui.screens.SearchScreen
import samachar.ai.ui.screens.SettingsScreen
import samachar.ai.ui.screens.SplashScreen
import samachar.ai.viewmodel.AppViewModel

object Routes {
    const val SPLASH = "splash"
    const val LOGIN = "login"
    const val ONBOARDING = "onboarding"
    const val HOME = "home"
    const val ARTICLE = "article"
    const val DISCOVER = "discover"
    const val PREMIUM = "premium"
    const val PROFILE = "profile"
    const val NOTIFICATIONS = "notifications"
    const val BOOKMARKS = "bookmarks"
    const val SEARCH = "search"
    const val AI = "ai"
    const val SETTINGS = "settings"
}

@Composable
fun AppNavGraph(vm: AppViewModel) {
    val nav = rememberNavController()
    val user by vm.user.collectAsState()
    val loading by vm.loading.collectAsState()
    val toastMsg by vm.toast.collectAsState()

    // Decide initial route
    val start = when {
        loading -> Routes.SPLASH
        user == null -> Routes.LOGIN
        user?.onboarded == false -> Routes.ONBOARDING
        else -> Routes.HOME
    }

    Box(modifier = Modifier.fillMaxSize()) {
        Scaffold(
            bottomBar = {
                val backStack by nav.currentBackStackEntryAsState()
                val current = backStack?.destination?.route
                val showTabs = current in setOf(
                    Routes.HOME, Routes.DISCOVER, Routes.PREMIUM, Routes.PROFILE
                )
                if (showTabs && user != null) {
                    TabBar(currentRoute = current ?: Routes.HOME) { tab ->
                        nav.navigate(tab) {
                            popUpTo(Routes.HOME); launchSingleTop = true
                        }
                    }
                }
            }
        ) { padding ->
            NavHost(
                navController = nav, startDestination = start,
                modifier = Modifier.padding(padding)
            ) {
                composable(Routes.SPLASH) { SplashScreen() }
                composable(Routes.LOGIN)  { LoginScreen(vm, nav) }
                composable(Routes.ONBOARDING) {
                    OnboardingScreen(vm) { nav.navigate(Routes.HOME) { popUpTo(0) } }
                }
                composable(Routes.HOME)          { HomeScreen(vm, nav) }
                composable(Routes.ARTICLE)       { ArticleScreen(vm, nav) }
                composable(Routes.DISCOVER)      { DiscoverScreen(vm, nav) }
                composable(Routes.PREMIUM)       { PremiumScreen(vm, nav) }
                composable(Routes.PROFILE)       { ProfileScreen(vm, nav) }
                composable(Routes.NOTIFICATIONS) { NotificationsScreen(vm, nav) }
                composable(Routes.BOOKMARKS)     { BookmarksScreen(vm, nav) }
                composable(Routes.SEARCH)        { SearchScreen(vm, nav) }
                composable(Routes.AI)            { AiChatScreen(vm, nav) }
                composable(Routes.SETTINGS)      { SettingsScreen(vm, nav) }
            }
        }
        Toast(message = toastMsg)
    }

    // Watch user state to redirect after sign-in / sign-out
    androidx.compose.runtime.LaunchedEffect(user, loading) {
        if (loading) return@LaunchedEffect
        val target = when {
            user == null -> Routes.LOGIN
            user?.onboarded == false -> Routes.ONBOARDING
            else -> Routes.HOME
        }
        val current = nav.currentDestination?.route
        // Only redirect if we're stuck on the wrong gate
        if (current == Routes.SPLASH ||
            (current == Routes.LOGIN && user != null) ||
            (current in setOf(Routes.HOME, Routes.DISCOVER, Routes.PREMIUM,
                              Routes.PROFILE, Routes.ARTICLE) && user == null)) {
            nav.navigate(target) { popUpTo(0) }
        }
    }
}

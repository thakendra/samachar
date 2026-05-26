package samachar.ai.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.Bookmark
import androidx.compose.material.icons.outlined.ChatBubbleOutline
import androidx.compose.material.icons.outlined.Share
import androidx.compose.material.icons.outlined.VerifiedUser
import androidx.compose.material3.Icon
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import samachar.ai.data.model.Article
import samachar.ai.ui.theme.MonoFamily
import samachar.ai.ui.theme.SamacharTheme
import samachar.ai.ui.theme.SansFamily
import samachar.ai.ui.theme.SerifFamily

@Composable
fun NewsCard(
    article: Article,
    bookmarked: Boolean,
    language: String,
    onOpen: () -> Unit,
    onBookmark: () -> Unit,
    onShare: () -> Unit,
    isLead: Boolean = false,
) {
    val palette = SamacharTheme.palette
    val title = if (language == "np" && !article.titleNp.isNullOrBlank()) article.titleNp!! else article.title

    Column(
        Modifier
            .fillMaxWidth()
            .clickable(onClick = onOpen)
            .padding(horizontal = 20.dp, vertical = 18.dp),
        verticalArrangement = Arrangement.spacedBy(10.dp),
    ) {
        if (isLead) {
            // Image placeholder
            Box(
                Modifier
                    .fillMaxWidth()
                    .aspectRatio(16f / 10f)
                    .clip(RoundedCornerShape(8.dp))
                    .background(palette.bgSunk),
                contentAlignment = Alignment.BottomStart,
            ) {
                Text(
                    article.imgLabel ?: "",
                    fontSize = 10.sp,
                    fontFamily = MonoFamily,
                    color = palette.ink3,
                    letterSpacing = 1.2.sp,
                    modifier = Modifier.padding(12.dp),
                )
            }
            // Meta line
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text(article.category, fontSize = 10.5.sp, fontFamily = MonoFamily,
                    fontWeight = FontWeight.SemiBold, color = palette.ink1, letterSpacing = 0.5.sp)
                MetaText("  ·  ${article.source}  ·  ${article.timeLabel}", color = palette.ink3)
            }
            Text(title, fontSize = 22.sp, fontFamily = SerifFamily,
                fontWeight = FontWeight.SemiBold, color = palette.ink1, lineHeight = 26.sp)
            Text(article.dek, fontSize = 13.5.sp, fontFamily = SansFamily,
                color = palette.ink2, lineHeight = 20.sp)
        } else {
            Row(horizontalArrangement = Arrangement.spacedBy(14.dp)) {
                Column(Modifier.weight(1f)) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Text(article.category, fontSize = 10.5.sp, fontFamily = MonoFamily,
                            fontWeight = FontWeight.SemiBold, color = palette.ink1, letterSpacing = 0.5.sp)
                        MetaText("  ·  ${article.source}  ·  ${article.timeLabel}", color = palette.ink3)
                    }
                    Spacer(Modifier.height(6.dp))
                    Text(title, fontSize = 17.sp, fontFamily = SerifFamily,
                        fontWeight = FontWeight.SemiBold, color = palette.ink1, lineHeight = 21.sp)
                    Spacer(Modifier.height(6.dp))
                    Text(article.dek, fontSize = 12.5.sp, color = palette.ink2,
                        lineHeight = 18.sp, maxLines = 2)
                }
                Box(
                    Modifier
                        .size(92.dp)
                        .clip(RoundedCornerShape(8.dp))
                        .background(palette.bgSunk)
                )
            }
        }
        // Footer
        Row(verticalAlignment = Alignment.CenterVertically) {
            if (article.verified) {
                Icon(Icons.Outlined.VerifiedUser, null,
                    tint = palette.verify, modifier = Modifier.size(12.dp))
                Spacer(Modifier.width(5.dp))
                MetaText("VERIFIED · ${article.verifiedCount}", color = palette.verify)
            }
            Spacer(Modifier.weight(1f))
            Row(verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(14.dp)) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(Icons.Outlined.ChatBubbleOutline, null,
                        tint = palette.ink3, modifier = Modifier.size(13.dp))
                    Spacer(Modifier.width(4.dp))
                    MetaText("${article.commentsCount}", color = palette.ink3)
                }
                Icon(Icons.Outlined.Bookmark, null,
                    tint = if (bookmarked) palette.accent else palette.ink3,
                    modifier = Modifier.size(13.dp).clickable(onClick = onBookmark))
                Icon(Icons.Outlined.Share, null,
                    tint = palette.ink3,
                    modifier = Modifier.size(13.dp).clickable(onClick = onShare))
            }
        }
        // Bottom rule
        Rule()
    }
}

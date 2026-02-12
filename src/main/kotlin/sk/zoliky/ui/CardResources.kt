package sk.zoliky.ui

import android.content.Context
import sk.zoliky.model.Card
import sk.zoliky.model.Rank
import sk.zoliky.model.Suit
import sk.zoliky.R

/**
 * Helper to retrieve drawable resource IDs for cards.
 * Pomocník pro získání ID drawable zdrojů pro karty.
 */
object CardResources {

    fun getCardResource(card: Card, context: Context): Int {
        if (card.rank == Rank.JOKER) {
            return R.drawable.joker
        }

        val suitPrefix = when (card.suit) {
            Suit.HEARTS -> "hearts"
            Suit.DIAMONDS -> "diamonds"
            Suit.CLUBS -> "clubs"
            Suit.SPADES -> "spades"
            Suit.NONE -> "" // Should not happen for non-joker / Nemělo by nastat
        }

        val rankSuffix = when (card.rank) {
            Rank.TWO -> "2"
            Rank.THREE -> "3"
            Rank.FOUR -> "4"
            Rank.FIVE -> "5"
            Rank.SIX -> "6"
            Rank.SEVEN -> "7"
            Rank.EIGHT -> "8"
            Rank.NINE -> "9"
            Rank.TEN -> "10"
            Rank.JACK -> "j"
            Rank.QUEEN -> "q"
            Rank.KING -> "k"
            Rank.ACE -> "a"
            Rank.JOKER -> "" // Handled above / Ošetřeno výše
        }

        val resourceName = "${suitPrefix}_${rankSuffix}"
        val resId = context.resources.getIdentifier(resourceName, "drawable", context.packageName)
        
        // Fallback to back of card if not found (should not happen in prod)
        // Záložní řešení (rub karty), pokud se nenajde (nemělo by nastat v produkci)
        return if (resId != 0) resId else R.drawable.blue_revers
    }
    
    fun getCardBackResource(): Int {
        return R.drawable.blue_revers
    }
}

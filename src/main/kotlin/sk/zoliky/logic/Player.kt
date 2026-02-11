package sk.zoliky.logic

import java.util.UUID

/**
 * Represents a player in the game.
 * Reprezentuje hráče ve hře.
 */
class Player(val name: String) {
    val id: String = UUID.randomUUID().toString()
    val hand = PlayerHand()
    var hasMelded: Boolean = false

    // Helper to check card count
    fun cardCount(): Int = hand.getCards().size

    // Helper to clear hand (for new game)
    fun clearHand() {
        // PlayerHand doesn't have clear(), need to recreate or implement clear?
        // Recreating is safer/easier.
        // Actually val hand = PlayerHand() is final.
        // Let's add clear() to PlayerHand or just remove all cards.
        val cards = hand.getCards()
        cards.forEach { hand.removeCard(it) }
    }
}

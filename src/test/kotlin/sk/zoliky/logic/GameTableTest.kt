package sk.zoliky.logic

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotEquals
import org.junit.Assert.assertTrue
import org.junit.Test
import sk.zoliky.model.Card
import sk.zoliky.model.Rank
import sk.zoliky.model.Suit
import java.lang.IllegalStateException

class GameTableTest {

    private val table = GameTable()

    @Test
    fun `startGame should initialize players and deal cards`() {
        val playerNames = listOf("Alice", "Bob")
        table.startGame(playerNames)

        // Verify players
        assertEquals(2, table.players.size)
        assertEquals("Alice", table.players[0].name)
        assertEquals("Bob", table.players[1].name)

        // Verify dealt cards
        // P1 should have 14 cards (Starter)
        assertEquals(14, table.players[0].hand.getCards().size)
        // P2 should have 13 cards
        assertEquals(13, table.players[1].hand.getCards().size)

        // Deck check: 108 total - 14 - 13 = 81 remaining
        assertEquals(81, table.deck.size())
        
        // Discard pile check
        assertTrue(table.discardPile.isEmpty())
        
        // Current player check (P1 starts)
        assertEquals(0, table.currentPlayerIndex)
    }

    @Test
    fun `turn progression should work correctly`() {
        table.startGame(listOf("Alice", "Bob"))
        val p1 = table.players[0]
        val p2 = table.players[1]

        // P1's turn
        assertEquals(p1, table.getCurrentPlayer())

        // P1 discards a card (simulated turn end)
        val cardToDiscard = p1.hand.getCards().first()
        table.discardCard(p1.id, cardToDiscard)

        // Should be P2's turn now
        assertEquals(p2, table.getCurrentPlayer())
        assertEquals(1, table.currentPlayerIndex)
        
        // Discard pile check
        assertEquals(1, table.discardPile.size)
        assertEquals(cardToDiscard, table.discardPile.last())
        
        // P1 hand size check (14 -> 13)
        assertEquals(13, p1.hand.getCards().size)
    }

    @Test
    fun `drawFromDiscard should take top card`() {
        table.startGame(listOf("Alice", "Bob"))
        val p1 = table.players[0]
        val p2 = table.players[1]

        // P1 discards -> P2's turn
        val card = p1.hand.getCards()[0]
        table.discardCard(p1.id, card)
        
        // P2 draws the discarded card
        table.drawFromDiscard(p2.id)
        
        // Verify P2 has the card
        assertTrue(p2.hand.getCards().contains(card))
        // Verify discard pile empty
        assertTrue(table.discardPile.isEmpty())
        // Verify P2 hand size (13 + 1 = 14)
        assertEquals(14, p2.hand.getCards().size)
    }

    @Test(expected = IllegalStateException::class)
    fun `acting out of turn should fail`() {
        table.startGame(listOf("Alice", "Bob"))
        val p2 = table.players[1]
        
        // It's P1's turn, P2 tries to draw
        table.drawCard(p2.id)
    }
}

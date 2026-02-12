package sk.zoliky.logic

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Assert.fail
import org.junit.Test
import sk.zoliky.model.Card
import sk.zoliky.model.Rank
import sk.zoliky.model.Suit

class GameTableTurnTest {

    private val table = GameTable()

    @Test
    fun `round number increases after full circle`() {
        table.startGame(listOf("Alice", "Bob"))
        
        // Round 1 Starts
        assertEquals(1, table.roundNumber)
        
        // Alice (Start) -> Ends turn
        endTurn(table.players[0].id) // Alice discards
        // Current: Bob
        
        // Bob -> Ends turn
        endTurn(table.players[1].id) // Bob discards
        // Current: Alice (Start again) -> Round should be 2
        
        assertEquals(2, table.roundNumber)
    }

    @Test
    fun `cannot draw from discard before round 4`() {
        table.startGame(listOf("Alice", "Bob"))
        table.setRoundForTesting(1)
        
        // P1 discards to put a card in discard pile
        val p1 = table.players[0]
        val card = p1.hand.getCards().first()
        table.discardCard(p1.id, card)
        
        // P2 tries to draw from discard in Round 1
        val p2 = table.players[1]
        try {
            table.drawFromDiscard(p2.id)
            fail("Should throw exception")
        } catch (e: IllegalStateException) {
            assertTrue(e.message?.contains("Round 4") == true)
        }
    }

    @Test
    fun `can draw from discard in round 4`() {
        table.startGame(listOf("Alice", "Bob"))
        table.setRoundForTesting(4)
        
        val p1 = table.getCurrentPlayer()
        
        // Ensure discard pile has a card
        table.discardPile.add(Card(Suit.HEARTS, Rank.ACE))
        
        // Try drawing from discard
        table.drawFromDiscard(p1.id)
        assertTrue(table.hasDrawnFromDiscard)
        assertTrue(p1.hand.getCards().last() == Card(Suit.HEARTS, Rank.ACE))
    }

    @Test
    fun `must meld after drawing from discard`() {
        table.startGame(listOf("Alice", "Bob"))
        table.setRoundForTesting(4)
        val p1 = table.getCurrentPlayer()
        
        // Prepare discard pile
        val card = Card(Suit.HEARTS, Rank.ACE)
        table.discardPile.add(card)
        
        // Draw
        table.drawFromDiscard(p1.id)
        
        // Try to discard without melding
        try {
            table.discardCard(p1.id, p1.hand.getCards().first())
            fail("Should throw exception")
        } catch (e: IllegalStateException) {
            assertTrue(e.message?.contains("Must meld") == true)
        }
    }

    @Test
    fun `can discard after melding when drawn from discard`() {
        table.startGame(listOf("Alice", "Bob"))
        table.setRoundForTesting(4)
        val p1 = table.getCurrentPlayer()
        
        // Clear hand completely
        while(p1.hand.getCards().isNotEmpty()) {
             p1.hand.removeCard(p1.hand.getCards()[0])
        }
        
        // Setup hand for a valid meld (> 42 points)
        // Meld 1: Hearts 10, J, Q (30 pts)
        p1.hand.addCard(Card(Suit.HEARTS, Rank.TEN))
        p1.hand.addCard(Card(Suit.HEARTS, Rank.JACK))
        p1.hand.addCard(Card(Suit.HEARTS, Rank.QUEEN))
        
        // Meld 2: Spades 10, J, Q (30 pts)
        p1.hand.addCard(Card(Suit.SPADES, Rank.TEN))
        p1.hand.addCard(Card(Suit.SPADES, Rank.JACK))
        p1.hand.addCard(Card(Suit.SPADES, Rank.QUEEN))
        
        p1.hand.addCard(Card(Suit.DIAMONDS, Rank.ACE)) // To discard
        
        // Add card to discard pile to draw
        table.discardPile.add(Card(Suit.CLUBS, Rank.TEN))
        
        // Action: Draw from discard
        table.drawFromDiscard(p1.id) 
        
        // Action: Meld both sequences
        val meld1 = listOf(
            Card(Suit.HEARTS, Rank.TEN),
            Card(Suit.HEARTS, Rank.JACK),
            Card(Suit.HEARTS, Rank.QUEEN)
        )
        val meld2 = listOf(
            Card(Suit.SPADES, Rank.TEN),
            Card(Suit.SPADES, Rank.JACK),
            Card(Suit.SPADES, Rank.QUEEN)
        )
        table.meld(p1.id, listOf(meld1, meld2))
        
        // Action: Discard Diamonds Ace
        table.discardCard(p1.id, Card(Suit.DIAMONDS, Rank.ACE))
        
        // Should succeed and turn ends
        assertFalse(table.hasDrawnFromDiscard) // Flags reset
    }

    private fun endTurn(playerId: String) {
        // Player draws (if not drawn)
        // Since we are mocking turns, we just ensure they have cards
        // In real game, they must draw.
        // table.drawCard(playerId)
        
        // Player discards
        val player = table.players.find { it.id == playerId }!!
        val card = player.hand.getCards().first()
        table.discardCard(playerId, card)
    }
}

package sk.zoliky.logic

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test
import sk.zoliky.model.Card
import sk.zoliky.model.Rank
import sk.zoliky.model.Suit
import java.lang.IllegalArgumentException
import java.lang.IllegalStateException

class MeldingTest {

    private val table = GameTable()

    // Helper
    private fun c(rank: Rank, suit: Suit) = Card(suit, rank)
    private fun joker() = Card(Suit.NONE, Rank.JOKER)

    @Test
    fun `initial meld should pass if restrictions met`() {
        val playerNames = listOf("Alice", "Bob")
        table.startGame(playerNames)
        val p1 = table.players[0]

        // Clear hand to setup specific scenario
        p1.hand.getCards().forEach { p1.hand.removeCard(it) }

        // Setup Valid Hand for Initial Meld (>= 42 pts + Pure Sequence)
        // Seq (Pure): Q, K, A Spades (31 pts)
        val seq = listOf(c(Rank.QUEEN, Suit.SPADES), c(Rank.KING, Suit.SPADES), c(Rank.ACE, Suit.SPADES))
        // Set: 7H, 7D, 7C (21 pts)
        val set = listOf(c(Rank.SEVEN, Suit.HEARTS), c(Rank.SEVEN, Suit.DIAMONDS), c(Rank.SEVEN, Suit.CLUBS))
        
        // Add to hand
        (seq + set).forEach { p1.hand.addCard(it) }

        // Perform Meld
        table.meld(p1.id, listOf(seq, set))

        // Verify
        assertTrue(p1.hasMelded)
        assertEquals(2, table.melds.size)
        assertEquals(0, p1.hand.getCards().size)
    }

    @Test(expected = IllegalArgumentException::class)
    fun `initial meld should fail if points too low`() {
        val playerNames = listOf("Alice", "Bob")
        table.startGame(playerNames)
        val p1 = table.players[0]
        p1.hand.getCards().forEach { p1.hand.removeCard(it) }

        // Low points: A, 2, 3 (6 pts) + 2, 2, 2 (6 pts) = 12 pts
        val seq = listOf(c(Rank.ACE, Suit.CLUBS), c(Rank.TWO, Suit.CLUBS), c(Rank.THREE, Suit.CLUBS))
        val set = listOf(c(Rank.TWO, Suit.HEARTS), c(Rank.TWO, Suit.DIAMONDS), c(Rank.TWO, Suit.SPADES))

        (seq + set).forEach { p1.hand.addCard(it) }

        table.meld(p1.id, listOf(seq, set))
    }
    
    @Test
    fun `addToMeld should work for valid cards`() {
        // Setup game state where P1 has already melded
        val playerNames = listOf("Alice", "Bob")
        table.startGame(playerNames)
        val p1 = table.players[0]
        p1.hand.getCards().forEach { p1.hand.removeCard(it) }
        
        val seq = listOf(c(Rank.QUEEN, Suit.SPADES), c(Rank.KING, Suit.SPADES), c(Rank.ACE, Suit.SPADES))
        val set = listOf(c(Rank.SEVEN, Suit.HEARTS), c(Rank.SEVEN, Suit.DIAMONDS), c(Rank.SEVEN, Suit.CLUBS))
        (seq + set).forEach { p1.hand.addCard(it) }
        table.meld(p1.id, listOf(seq, set))
        
        // Now add a card to the Set (7 Spades)
        val card7S = c(Rank.SEVEN, Suit.SPADES)
        p1.hand.addCard(card7S)
        
        // Find set index (should be 1, since seq added first? List order preserved)
        // Melds[0] = Seq, Melds[1] = Set
        val setIndex = 1
        
        table.addToMeld(p1.id, setIndex, card7S)
        
        // Verify
        assertEquals(4, table.melds[setIndex].size)
        assertFalse(p1.hand.getCards().contains(card7S))
    }

    @Test
    fun `replaceJoker should swap card and return Joker to hand`() {
        // Setup game state with Joker in meld
        val playerNames = listOf("Alice", "Bob")
        table.startGame(playerNames)
        val p1 = table.players[0]
        p1.hand.getCards().forEach { p1.hand.removeCard(it) }

        // Seq: 7, Joker, 9 (Diamonds)
        val joker = joker()
        val seq = listOf(c(Rank.SEVEN, Suit.DIAMONDS), joker, c(Rank.NINE, Suit.DIAMONDS))
        // Set to meet points: Q, K, A (31 pts)
        val set = listOf(c(Rank.QUEEN, Suit.CLUBS), c(Rank.KING, Suit.CLUBS), c(Rank.ACE, Suit.CLUBS))
        
        (seq + set).forEach { p1.hand.addCard(it) }
        table.meld(p1.id, listOf(seq, set))
        
        // Player gets 8 Diamonds
        val card8D = c(Rank.EIGHT, Suit.DIAMONDS)
        p1.hand.addCard(card8D)
        
        // Replace Joker
        table.replaceJoker(p1.id, 0, joker, card8D)
        
        // Verify
        // Meld should be 7, 8, 9
        val meld = table.melds[0]
        assertEquals(card8D, meld[1])
        assertFalse(meld.contains(joker))
        
        // Player hand should have Joker and NO 8D
        assertTrue(p1.hand.getCards().contains(joker))
        assertFalse(p1.hand.getCards().contains(card8D))
    }
}

package sk.zoliky.logic

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test
import sk.zoliky.model.Card
import sk.zoliky.model.Rank
import sk.zoliky.model.Suit

class PlayerHandTest {

    private val hand = PlayerHand()

    // Helper
    private fun c(rank: Rank, suit: Suit) = Card(suit, rank)
    private fun joker() = Card(Suit.NONE, Rank.JOKER)

    @Test
    fun `addCard should add card to hand`() {
        hand.addCard(c(Rank.ACE, Suit.SPADES))
        assertEquals(1, hand.getCards().size)
        assertEquals(c(Rank.ACE, Suit.SPADES), hand.getCards()[0])
    }

    @Test
    fun `removeCard should remove card from hand`() {
        val card = c(Rank.ACE, Suit.SPADES)
        hand.addCard(card)
        assertTrue(hand.removeCard(card))
        assertEquals(0, hand.getCards().size)
    }

    @Test
    fun `sortCards should sort by Suit then Rank`() {
        val c1 = c(Rank.KING, Suit.HEARTS)
        val c2 = c(Rank.TWO, Suit.HEARTS)
        val c3 = c(Rank.TEN, Suit.CLUBS)

        // Add in random order
        hand.addCard(c1)
        hand.addCard(c2)
        hand.addCard(c3)

        // Expected sorted order (Suit order: HEARTS, DIAMONDS, CLUBS, SPADES):
        // 1. HEARTS 2 (c2)
        // 2. HEARTS KING (c1)
        // 3. CLUBS 10 (c3)
        // But wait, Enum order is H, D, C, S.
        // H 2, H K, C 10. Correct.

        hand.sortCards(bySuit = true)
        val sorted = hand.getCards()

        // Kotlin verify:
        // H < D, H < C, H < S
        // Within H: 2 < K
        
        // Let's verify exact contents
        assertTrue(sorted.contains(c1))
        assertTrue(sorted.contains(c2))
        assertTrue(sorted.contains(c3))
        
        // Verify primary sort (Suit)
        assertEquals(Suit.HEARTS, sorted[0].suit)
        assertEquals(Suit.HEARTS, sorted[1].suit)
        assertEquals(Suit.CLUBS, sorted[2].suit)
        
        // Verify secondary sort (Rank)
        assertEquals(Rank.TWO, sorted[0].rank)
        assertEquals(Rank.KING, sorted[1].rank)
    }

    @Test
    fun `canMeld should validate correctly`() {
        // Prepare combinations helper
        val seqLow = listOf(c(Rank.ACE, Suit.CLUBS), c(Rank.TWO, Suit.CLUBS), c(Rank.THREE, Suit.CLUBS))
        val seqHigh = listOf(c(Rank.QUEEN, Suit.SPADES), c(Rank.KING, Suit.SPADES), c(Rank.ACE, Suit.SPADES))
        val set7 = listOf(c(Rank.SEVEN, Suit.HEARTS), c(Rank.SEVEN, Suit.DIAMONDS), c(Rank.SEVEN, Suit.CLUBS))
        
        // 1. Invalid: Too few points (6 pts)
        assertFalse(hand.canMeld(listOf(seqLow))) 

        // 2. Valid: Pure Seq (31 pts) + Set (21 pts) = 52 pts. >= 42. Pure seq present.
        assertTrue(hand.canMeld(listOf(seqHigh, set7)))

        // 3. Invalid: High points but NO pure sequence
        // Seq with Joker (24 pts)
        val seqJoker = listOf(c(Rank.SEVEN, Suit.DIAMONDS), joker(), c(Rank.NINE, Suit.DIAMONDS))
        // Set with Joker (30 pts)
        val setJoker = listOf(c(Rank.KING, Suit.HEARTS), c(Rank.KING, Suit.CLUBS), joker())
        
        assertFalse(hand.canMeld(listOf(seqJoker, setJoker)))
        
        // 4. Invalid: Pure Sequence present but points too low (12 total)
        val set2 = listOf(c(Rank.TWO, Suit.HEARTS), c(Rank.TWO, Suit.DIAMONDS), c(Rank.TWO, Suit.CLUBS))
        assertFalse(hand.canMeld(listOf(seqLow, set2)))
        
        // 5. Invalid: Contains broken set
        val invalidSet = listOf(c(Rank.SEVEN, Suit.HEARTS), c(Rank.EIGHT, Suit.DIAMONDS))
        assertFalse(hand.canMeld(listOf(seqHigh, invalidSet)))
    }
}

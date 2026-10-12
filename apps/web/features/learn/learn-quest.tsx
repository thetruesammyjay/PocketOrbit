"use client";

import Image from "next/image";
import { useEffect, useState } from "react";

const questions = [
  {
    topic: "Asset identity",
    question: "Two tokens are both called ORBIT. What best tells them apart?",
    answers: [
      "Their symbol and color",
      "Their network and contract address",
      "The wallet that holds them"
    ],
    correct: 1,
    explanation: "Symbols can be reused. A token’s network and contract address identify which asset a record refers to."
  },
  {
    topic: "Freshness",
    question: "A balance was checked yesterday. What should you look at before relying on it?",
    answers: [
      "Its source and last-updated time",
      "Whether the number has many decimals",
      "Whether another asset has the same symbol"
    ],
    correct: 0,
    explanation: "A timestamp helps you judge freshness. It tells you when PocketOrbit retrieved the reading, not that the provider guarantees it is correct."
  },
  {
    topic: "Stablecoins",
    question: "A stablecoin aims to track one dollar. Which statement is accurate?",
    answers: [
      "It is guaranteed to always be worth one dollar",
      "It is designed to track a value, but its price can move",
      "It cannot lose its peg if it is on a major network"
    ],
    correct: 1,
    explanation: "‘Stable’ describes the target, not a guarantee. Market prices can move away from that target."
  },
  {
    topic: "Network fees",
    question: "What does a network fee pay for?",
    answers: [
      "Processing an action on a blockchain",
      "Keeping a portfolio dashboard online",
      "Converting every token to dollars"
    ],
    correct: 0,
    explanation: "A network fee is associated with processing an on-chain action. It is separate from PocketOrbit, which is read-only and does not move assets."
  },
  {
    topic: "Transfers",
    question: "You move tokens between two wallets you own. How should that be treated?",
    answers: [
      "As a buy and a sell by default",
      "As a possible internal transfer, matched only with enough evidence",
      "As income because the destination received tokens"
    ],
    correct: 1,
    explanation: "An own-wallet transfer is not automatically a trade. Reliable matching needs evidence that both sides belong to you."
  },
  {
    topic: "Portfolio coverage",
    question: "A wallet sync returns some tokens but reports that token discovery was incomplete. What is the honest label?",
    answers: [
      "Complete portfolio",
      "Partial coverage, with missing data disclosed",
      "Zero balance for anything it did not return"
    ],
    correct: 1,
    explanation: "An incomplete scan cannot establish a complete total. Missing data should stay visible instead of being treated as zero."
  },
  {
    topic: "Performance",
    question: "A balance is worth more today than last month. Is that enough to know your profit?",
    answers: [
      "Yes, the value increase is your profit",
      "Only if the asset is a stablecoin",
      "No. You also need transaction history and a stated cost-basis method"
    ],
    correct: 2,
    explanation: "A balance snapshot shows what is held now. Accurate realized or unrealized performance also depends on history, cost basis, and the method used."
  },
  {
    topic: "Reporting currency",
    question: "If you switch the dashboard from USD to EUR, what changes?",
    answers: [
      "The displayed value conversion; token quantities stay the same",
      "The amount of crypto in your wallets",
      "The wallet’s transaction history"
    ],
    correct: 0,
    explanation: "Reporting currency changes how values are displayed. It does not change the underlying token amounts."
  }
] as const;

const fieldNotes = [
  {
    title: "A snapshot is not a transaction history",
    text: "A wallet balance answers ‘what is here now?’ It does not explain every deposit, trade, fee, or withdrawal that led to it."
  },
  {
    title: "Freshness and confidence are different",
    text: "A recent reading can still have incomplete coverage. Check both when it was updated and what the source could actually see."
  },
  {
    title: "Price change is not the whole P&L",
    text: "Performance needs transaction history, a cost-basis method, and clear treatment of fees and transfers. A current balance alone is not enough."
  },
  {
    title: "Read-only means no asset control",
    text: "A public address can be used to read public blockchain data. It cannot authorize PocketOrbit to send funds, and no seed phrase is needed."
  }
];

const scoreStorageKey = "pocketorbit.learn.best-round.v1";

export function LearnQuest() {
  const [questionIndex, setQuestionIndex] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState<number | null>(null);
  const [score, setScore] = useState(0);
  const [bestScore, setBestScore] = useState(0);
  const [finished, setFinished] = useState(false);

  useEffect(() => {
    try {
      const savedScore = Number(window.localStorage.getItem(scoreStorageKey));
      if (Number.isFinite(savedScore) && savedScore > 0) setBestScore(savedScore);
    } catch {
      // The learning round still works when browser storage is unavailable.
    }
  }, []);

  useEffect(() => {
    if (!finished) return;
    const nextBest = Math.max(bestScore, score);
    setBestScore(nextBest);
    try {
      window.localStorage.setItem(scoreStorageKey, String(nextBest));
    } catch {
      // Scores are a local encouragement, not required account data.
    }
  }, [bestScore, finished, score]);

  const currentQuestion = questions[questionIndex];
  const answeredCount = questionIndex + (selectedAnswer === null ? 0 : 1);
  const progress = finished ? 1 : answeredCount / questions.length;

  function chooseAnswer(answerIndex: number) {
    if (selectedAnswer !== null) return;
    setSelectedAnswer(answerIndex);
    if (answerIndex === currentQuestion.correct) setScore((value) => value + 25);
  }

  function continueRound() {
    if (selectedAnswer === null) return;
    if (questionIndex === questions.length - 1) {
      setFinished(true);
      return;
    }
    setQuestionIndex((value) => value + 1);
    setSelectedAnswer(null);
  }

  function replayRound() {
    setQuestionIndex(0);
    setSelectedAnswer(null);
    setScore(0);
    setFinished(false);
  }

  return (
    <div className="learn-experience">
      <section className="learn-quest panel" aria-label="Portfolio data quiz">
        <div className="learn-quest-topline">
          <div className="learn-quest-identity">
            <Image src="/brand/pocketorbit-comet.png" alt="" aria-hidden="true" width={120} height={120} />
            <div>
              <span className="learn-quest-kicker">Orbit field guide</span>
              <h2>Data detective</h2>
            </div>
          </div>
          <div className="learn-scoreboard" aria-label={`Best round: ${bestScore} points`}>
            <span>Best round</span>
            <strong>{bestScore} <small>XP</small></strong>
          </div>
        </div>

        <p className="learn-quest-intro">Read the clues, choose the clearest answer, and build a sharper picture of what your portfolio data can tell you.</p>

        <div className="learn-progress-row">
          <span>{finished ? "Round complete" : `Checkpoint ${questionIndex + 1} of ${questions.length}`}</span>
          <span>{score} XP</span>
        </div>
        <div className="learn-progress-track" role="progressbar" aria-label="Round progress" aria-valuemin={0} aria-valuemax={questions.length} aria-valuenow={finished ? questions.length : answeredCount}>
          <span style={{ transform: `scaleX(${progress})` }} />
        </div>

        {finished ? (
          <div className="learn-complete" aria-live="polite">
            <span className="learn-complete-mark" aria-hidden="true">✦</span>
            <div>
              <p className="learn-quest-kicker">Your field notes are sharper</p>
              <h3>{score} XP earned</h3>
              <p>You finished all {questions.length} checkpoints. Your best round is saved in this browser.</p>
              <button className="button button--primary" type="button" onClick={replayRound}>Play another round</button>
            </div>
          </div>
        ) : (
          <div className="learn-challenge" aria-live="polite">
            <div className="learn-challenge-copy">
              <span className="badge badge--violet">{currentQuestion.topic}</span>
              <h3>{currentQuestion.question}</h3>
            </div>
            <div className="learn-answer-list" role="group" aria-label="Choose an answer">
              {currentQuestion.answers.map((answer, index) => {
                const isSelected = selectedAnswer === index;
                const isCorrect = index === currentQuestion.correct;
                const resultClass = selectedAnswer === null ? "" : isCorrect ? " learn-answer--correct" : isSelected ? " learn-answer--incorrect" : "";
                return (
                  <button
                    className={`learn-answer${resultClass}`}
                    type="button"
                    key={answer}
                    aria-pressed={isSelected}
                    onClick={() => chooseAnswer(index)}
                  >
                    <span className="learn-answer-letter" aria-hidden="true">{String.fromCharCode(65 + index)}</span>
                    <span>{answer}</span>
                  </button>
                );
              })}
            </div>

            {selectedAnswer !== null && (
              <div className={`learn-answer-feedback ${selectedAnswer === currentQuestion.correct ? "learn-answer-feedback--correct" : "learn-answer-feedback--incorrect"}`}>
                <strong>{selectedAnswer === currentQuestion.correct ? "Good read. +25 XP" : "Good clue to remember."}</strong>
                <p>{currentQuestion.explanation}</p>
              </div>
            )}

            <div className="learn-quest-footer">
              <p>Points stay in this browser; they have no token or cash value.</p>
              <button className="button button--primary" type="button" disabled={selectedAnswer === null} onClick={continueRound}>
                {questionIndex === questions.length - 1 ? "See my result" : "Next checkpoint"}
              </button>
            </div>
          </div>
        )}
      </section>

      <section className="learn-field-notes" aria-labelledby="learn-field-notes-title">
        <div className="learn-section-heading">
          <div>
            <p className="learn-quest-kicker">PocketOrbit principles</p>
            <h2 id="learn-field-notes-title">Field notes for a clearer view</h2>
          </div>
          <p>Open a note for a quick fact you can use while reading your portfolio.</p>
        </div>
        <div className="learn-note-list">
          {fieldNotes.map((note, index) => (
            <details className="learn-note panel" key={note.title}>
              <summary>
                <span className={`learn-note-index learn-note-index--${index + 1}`}>0{index + 1}</span>
                <span>{note.title}</span>
                <span className="learn-note-toggle" aria-hidden="true">+</span>
              </summary>
              <p>{note.text}</p>
            </details>
          ))}
        </div>
      </section>
    </div>
  );
}

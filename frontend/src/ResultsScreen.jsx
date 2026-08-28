import { useEffect, useRef } from "react";

const ADVISER_LINK = "https://www.lease-advice.org/contact-us/";
const ALL_TOPICS_LINK = "https://www.lease-advice.org/";

function CategoryDetails({ category, showName }) {
	return (
		<div className="category-details">
			{showName && <h3>{category.name}</h3>}
			{category.is_urgent && (
				<p className="urgent-note">
					This may be urgent — please don't wait to get advice.
				</p>
			)}
			<p>{category.summary}</p>
			<p>{category.next_step}</p>
			{category.guide_link && (
				<p>
					<a href={category.guide_link} target="_blank" rel="noreferrer">
						Read the full guide
						<span className="visually-hidden"> (opens in a new tab)</span>
					</a>
				</p>
			)}
		</div>
	);
}

function ResultsScreen({ result }) {
	const headingRef = useRef(null);

	useEffect(() => {
		headingRef.current?.focus();
	}, [result]);

	const { confident, matches } = result;
	const ambiguous = confident && matches.length > 1;

	let heading = "This looks like:";
	if (!confident) {
		heading = "We're not sure — let's get you to a human";
	} else if (ambiguous) {
		heading = "A few things this could be";
	}

	return (
		<section aria-labelledby="result-heading">
			<h2 id="result-heading" tabIndex={-1} ref={headingRef}>
				{heading}
			</h2>

			{confident && !ambiguous && (
				<CategoryDetails category={matches[0].category} showName />
			)}

			{ambiguous && (
				<div className="ambiguous-matches">
					<p>
						We found more than one possible match. Take a look and pick
						whichever sounds closest to your situation:
					</p>
					{matches.map((match) => (
						<CategoryDetails
							key={match.category.slug}
							category={match.category}
							showName
						/>
					))}
				</div>
			)}

			{!confident && <CategoryDetails category={matches[0].category} />}

			<div className="escape-hatch">
				<p>
					Whatever your situation, you can always{" "}
					<a href={ADVISER_LINK} target="_blank" rel="noreferrer">
						speak to an adviser
						<span className="visually-hidden"> (opens in a new tab)</span>
					</a>{" "}
					or{" "}
					<a href={ALL_TOPICS_LINK} target="_blank" rel="noreferrer">
						browse all topics
						<span className="visually-hidden"> (opens in a new tab)</span>
					</a>
					.
				</p>
			</div>
		</section>
	);
}

export default ResultsScreen;

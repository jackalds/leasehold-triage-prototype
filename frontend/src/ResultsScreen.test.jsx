import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import ResultsScreen from "./ResultsScreen.jsx";

function category(overrides = {}) {
	return {
		slug: "service-charges",
		name: "Service charges",
		summary: "This usually means...",
		next_step: "Read the guide.",
		guide_link: "https://www.lease-advice.org/service-charges",
		is_urgent: false,
		...overrides,
	};
}

describe("ResultsScreen", () => {
	it("renders a single confident match", () => {
		render(
			<ResultsScreen
				result={{
					confident: true,
					matches: [{ category: category(), confidence: 0.95 }],
				}}
			/>
		);

		expect(screen.getByText("This looks like:")).toBeInTheDocument();
		expect(screen.getByText("Service charges")).toBeInTheDocument();
		expect(screen.getByText("This usually means...")).toBeInTheDocument();
	});

	it("shows an urgent note for urgent categories", () => {
		render(
			<ResultsScreen
				result={{
					confident: true,
					matches: [{ category: category({ is_urgent: true }), confidence: 0.95 }],
				}}
			/>
		);

		expect(
			screen.getByText("This may be urgent — please don't wait to get advice.")
		).toBeInTheDocument();
	});

	it("renders every match when the result is ambiguous", () => {
		render(
			<ResultsScreen
				result={{
					confident: true,
					matches: [
						{ category: category(), confidence: 0.6 },
						{
							category: category({ slug: "ground-rent", name: "Ground rent" }),
							confidence: 0.5,
						},
					],
				}}
			/>
		);

		expect(screen.getByText("A few things this could be")).toBeInTheDocument();
		expect(screen.getByText("Service charges")).toBeInTheDocument();
		expect(screen.getByText("Ground rent")).toBeInTheDocument();
	});

	it("routes the not-sure outcome to a human without a category name", () => {
		render(
			<ResultsScreen
				result={{
					confident: false,
					matches: [
						{ category: category({ slug: "not-sure", name: "Not sure" }), confidence: 0 },
					],
				}}
			/>
		);

		expect(
			screen.getByText("We're not sure — let's get you to a human")
		).toBeInTheDocument();
		expect(screen.queryByRole("heading", { name: "Not sure" })).not.toBeInTheDocument();
	});

	it("always shows the adviser and browse-all-topics escape hatch", () => {
		render(
			<ResultsScreen
				result={{
					confident: false,
					matches: [{ category: category(), confidence: 0 }],
				}}
			/>
		);

		expect(
			screen.getByRole("link", { name: /speak to an adviser/ })
		).toHaveAttribute("href", "https://www.lease-advice.org/contact-us/");
		expect(
			screen.getByRole("link", { name: /browse all topics/ })
		).toHaveAttribute("href", "https://www.lease-advice.org/");
	});

	it("moves focus to the results heading so screen reader and keyboard users land on it", () => {
		render(
			<ResultsScreen
				result={{
					confident: true,
					matches: [{ category: category(), confidence: 0.95 }],
				}}
			/>
		);

		expect(screen.getByRole("heading", { name: "This looks like:" })).toHaveFocus();
	});
});

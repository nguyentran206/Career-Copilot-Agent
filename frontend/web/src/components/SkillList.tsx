interface SkillListProps {
  items: string[];
  variant?: "matched" | "missing";
  emptyText: string;
}

export function SkillList({
  items,
  variant = "matched",
  emptyText
}: SkillListProps) {
  if (items.length === 0) {
    return <p>{emptyText}</p>;
  }

  return (
    <ul className="skill-list">
      {items.map((item) => (
        <li
          className={`skill-pill ${variant === "missing" ? "missing" : ""}`}
          key={item}
        >
          {item}
        </li>
      ))}
    </ul>
  );
}

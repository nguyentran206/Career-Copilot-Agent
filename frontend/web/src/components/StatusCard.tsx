interface StatusCardProps {
  title: string;
  description: string;
  showSpinner?: boolean;
}

export function StatusCard({
  title,
  description,
  showSpinner = false
}: StatusCardProps) {
  return (
    <div className="card status-card">
      {showSpinner ? <div className="spinner" aria-hidden="true" /> : null}
      <h2>{title}</h2>
      <p className="hint">{description}</p>
    </div>
  );
}

interface BadgeProps {
  children: React.ReactNode;
  color?: string;
}

export function Badge({ children, color = "bg-gray-100 text-gray-800" }: BadgeProps) {
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${color}`}>
      {children}
    </span>
  );
}

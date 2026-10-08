export type UserRole="admin"|"manager"|"operator"|"viewer";
export const roleLabels:Record<UserRole,string>={admin:"Administrator",manager:"Farm Manager",operator:"Operator",viewer:"Viewer"};
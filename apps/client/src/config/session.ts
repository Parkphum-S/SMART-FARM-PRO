import type { UserRole } from "./roles";
export type AppUser={id:string;displayName:string;role:UserRole};
export const currentUser:AppUser={id:"shell-user",displayName:"Smart Farm User",role:"admin"};
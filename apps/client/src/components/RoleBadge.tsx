import { StyleSheet, Text, View } from "react-native";
import { roleLabels,type UserRole } from "@/config/roles";
export function RoleBadge({role}:{role:UserRole}){return <View style={styles.badge}><Text style={styles.text}>{roleLabels[role]}</Text></View>}
const styles=StyleSheet.create({badge:{borderRadius:999,paddingHorizontal:12,paddingVertical:8,backgroundColor:"#E4ECE2"},text:{fontSize:12,fontWeight:"700",color:"#315037"}});
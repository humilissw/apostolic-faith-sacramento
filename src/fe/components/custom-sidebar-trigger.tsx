'use client'

import { useSidebar } from "@/components/ui/sidebar"
import { AiOutlineMenu } from "react-icons/ai";
import { IoMdClose } from "react-icons/io";

interface TriggerProps {
    state: boolean;
}
 
export default function CustomSidebarTrigger(props: TriggerProps) {
  const { toggleSidebar } = useSidebar()
  
  return (
    <button aria-label={props.state ? "Close Menu" : "Open Menu"} onClick={toggleSidebar}>
        {props.state ? (<IoMdClose size="30"/>) : (<AiOutlineMenu size="30"/>)}
    </button>
  )
}
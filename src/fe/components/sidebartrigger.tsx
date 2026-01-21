'use client'

import { useSidebar } from "@/components/ui/sidebar"
import Hamburger from 'hamburger-react';
import { useState } from "react";

import { AiOutlineMenu } from "react-icons/ai";
import { IoMdClose } from "react-icons/io";


interface TriggerProps {
    state: boolean;
}
 
export default function CustomTrigger(props: TriggerProps) {
  const { toggleSidebar } = useSidebar()
  
  return (
    <button onClick={toggleSidebar}>
        {props.state ? (<IoMdClose size="30"/>) : (<AiOutlineMenu size="30"/>)}
    </button>
  )
}
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { useAuth } from "@/context/auth-context";
import { CircleUserRound } from "lucide-react"

export function ProfileDropdown() {
    const auth = useAuth();

    return (
        <DropdownMenu>
        <DropdownMenuTrigger asChild>
            <Button
                variant="outline"
                size="sm"
                >
                <CircleUserRound />
            </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent>
            <DropdownMenuGroup>
            <DropdownMenuLabel>My Account</DropdownMenuLabel>
            <DropdownMenuItem onClick={() => auth.logout()}>Log out</DropdownMenuItem>
            </DropdownMenuGroup>
        </DropdownMenuContent>
        </DropdownMenu>
    )
}

import { IconProps } from "../types"
import conversationSvg from "@/assets/conversation.svg?react"

interface IConversationIconProps extends IconProps {
  active?: boolean
}

export const ConversationIcon = (props: IConversationIconProps) => {
  const { active, ...rest } = props

  const color = active ? "#3D53F5" : "#667085"

  return conversationSvg({
    color,
    ...rest,
  })
}

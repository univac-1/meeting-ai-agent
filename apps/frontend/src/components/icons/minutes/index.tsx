import minutesSvg from "@/assets/minutes.svg?react"
import { IconProps } from "../types"

interface IMinutesIconProps extends IconProps {
  active?: boolean
}

export const MinutesIcon = (props: IMinutesIconProps) => {
  const { active, ...rest } = props
  const color = active ? "#3D53F5" : "#667085"

  return minutesSvg({
    color,
    ...rest,
  })
}

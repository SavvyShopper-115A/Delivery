import type { User } from "firebase/auth"

export interface ItemType {
  desired_price: number
  item_name: string
  price_data: number[]
  retailer: {
    icon: string
    name: string
  }
  start_date: string
  uid: string
  id: string
  url: string
  status: "processing" | "stopped" | "completed"
  nickname: string
}

export const postAddItem = async (item: ItemType, user: User) => {
  const fullURL = `${process.env.PLASMO_PUBLIC_API_URI}/schedule`

  const accessToken = await user.getIdToken();

  const response = await fetch(fullURL, {
    method: "POST",
    body: JSON.stringify(item),
    headers: {
      Authorization: accessToken,
      "Content-Type": "application/json"
    }
  })

  if (!response.ok) {
    const errorData = await response.json()
    throw new Error(errorData.error)
  }

  const data = await response.json()

  return data
}

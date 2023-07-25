import { Button, Image, Input, Loading, Spacer } from "@nextui-org/react"
import { useEffect, useState } from "react"
import useSWR from "swr"
import NavbarComponent from "~components/Navbar"

import { getDataFromURL } from "~core/get-data-from-url"
import { postAddItem, type ItemType } from "~core/post-add-item"
import { useFirebase } from "~firebase/hook"

interface URLSuccessResponse {
  name: string
  price: number
  retailer: {
    name: string
    icon: string
  }
}

export default function IndexPopup() {
  const { user, isLoading } = useFirebase()

  const [currentTabUrl, setCurrentTabUrl] = useState<string | null>(null);
  const [desiredPrice, setDesiredPrice] = useState(0);
  const [nickname, setNickname] = useState('');

  useEffect(() => {
    chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
      const { url } = tabs[0];
      setCurrentTabUrl(url);
    });
  }, []);

  const { data, error } = useSWR<URLSuccessResponse>(
    currentTabUrl,
    getDataFromURL
  )

  if (error) {
    return <div>Error occurred: {error.message} current tab url: {currentTabUrl}</div>
  }

  if (!data) {
    return <div style={{padding: 15}}><Loading /></div>
  }

  return (
    <div>
      <NavbarComponent />

      <div
      style={{
        display: "flex",
        flexDirection: "column",
        padding: 16,
        width: 400
      }}>
      <div>
        {isLoading ? "Loading..." : ""}
        {!!user ? (
          <div style={{ marginTop: "1rem" }}>
            <div style={{ display: "flex", flexDirection: "row" }}>
              <img
                src={data.retailer.icon}
                alt="retailer icon"
                style={{ width: 50, height: 50, objectFit: 'contain' }}
              />
              <Spacer x={1} />
              <div>{data.name}</div>
            </div>
            <Spacer y={1} />
            <div style={{ display: "flex", flexDirection: "row" }}>
              <Input
                labelLeft={"$"}
                disabled
                placeholder={data.price.toFixed()}
                label="Current Price"
              />
              <Spacer x={1} />
              <Input
                labelLeft={"$"}
                type="number"
                required
                helperText="Required"
                placeholder="0"
                label="Desired Price"
                step="0.01"
                min="0"
                pattern="^\$[0-9]+(\.[0-9]{0,2})?$"
                value={desiredPrice}
                onChange={(event) => {
                  const newPrice = parseFloat(
                    parseFloat(event.target.value).toFixed(2)
                  )
                  setDesiredPrice(newPrice);
                }}
              />
            </div>
            <Spacer y={0.5} />
            <Input
              width="100%"
              label="Name"
              value={nickname}
              onChange={(event) => {
                setNickname(event.target.value);
              }}
            />

            <Spacer y={1} />

            <Button
              auto
              style={{width: 400}}
              onPress={() => {
                const item = {
                  desired_price: desiredPrice,
                  item_name: data.name,
                  price_data: [data.price],
                  retailer: {
                    icon: data.retailer.icon,
                    name: data.retailer.name
                  },
                  start_date: new Date().toISOString(),
                  url: currentTabUrl,
                  status: "processing",
                  nickname: nickname

                } as ItemType;
                postAddItem(item, user).then(() => {
                  window.close()
                }).catch(() => {
                  window.close()
                });
              }}
              disabled={desiredPrice === 0}>
              Add Task
            </Button>
          </div>
        ) : (
          ""
        )}
      </div>
    </div>
    </div>
    
  )
}

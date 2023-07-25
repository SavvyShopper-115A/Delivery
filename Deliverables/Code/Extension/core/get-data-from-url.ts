export const getDataFromURL = async (url: string | null) => {
    if (url == null) {
      return null;
    }
    const fullURL = `${process.env.PLASMO_PUBLIC_API_URI}/search?url=${url}`;
  
    const response = await fetch(fullURL, {
      method: "GET",
    });

    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error);
    }

    const data = await response.json();

    return data;
  };
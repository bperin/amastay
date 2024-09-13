import { serve } from "https://deno.land/std@0.114.0/http/server.ts";

// The function to handle HTTP requests
serve(async (req: Request) => {
  try {
    const { url, property_id } = await req.json();

    if (!url || !property_id) {
      return new Response(
        JSON.stringify({ error: "Missing url or property_id" }),
        { status: 400 }
      );
    }

    // Implement your scraping logic here (e.g., fetch the page content)
    const response = await fetch(url);
    const pageContent = await response.text();

    // Add logic to upload to Supabase or return scraped content
    // Example: Just returning the scraped content for now
    return new Response(
      JSON.stringify({
        message: "Scraping successful",
        data: pageContent.substring(0, 200), // Returning only part of the content for brevity
      }),
      { status: 200 }
    );
  } catch (error) {
    return new Response(
      JSON.stringify({ error: error.message || "An error occurred" }),
      { status: 500 }
    );
  }
});

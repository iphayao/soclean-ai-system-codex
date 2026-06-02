"use client";

import { Save, Upload } from "lucide-react";
import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";

import { api, Brand, Campaign, Product } from "@/app/lib/api";

export function BrandMemoryForm({ brand }: { brand: Brand | null }) {
  const router = useRouter();
  const [message, setMessage] = useState<string | null>(null);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const payload = {
      name: String(form.get("name") || "SoClean"),
      slug: String(form.get("slug") || "soclean"),
      description: String(form.get("description") || ""),
      voice: String(form.get("voice") || ""),
      compliance_notes: String(form.get("compliance_notes") || ""),
    };
    if (brand) {
      await api.updateBrand(brand.id, payload);
    } else {
      await api.createBrand(payload);
    }
    setMessage("Brand memory saved.");
    router.refresh();
  }

  return (
    <form className="form" onSubmit={submit}>
      <div className="form-grid">
        <div className="field">
          <label htmlFor="name">Brand name</label>
          <input id="name" name="name" defaultValue={brand?.name ?? "SoClean"} required />
        </div>
        <div className="field">
          <label htmlFor="slug">Slug</label>
          <input id="slug" name="slug" defaultValue={brand?.slug ?? "soclean"} required />
        </div>
      </div>
      <div className="field">
        <label htmlFor="description">Description</label>
        <textarea id="description" name="description" defaultValue={brand?.description ?? ""} />
      </div>
      <div className="field">
        <label htmlFor="voice">Voice</label>
        <textarea id="voice" name="voice" defaultValue={brand?.voice ?? ""} />
      </div>
      <div className="field">
        <label htmlFor="compliance_notes">Compliance notes</label>
        <textarea id="compliance_notes" name="compliance_notes" defaultValue={brand?.compliance_notes ?? ""} />
      </div>
      <div className="actions">
        <button type="submit">
          <Save size={16} aria-hidden="true" />
          Save Brand Memory
        </button>
        {message ? <span className="muted">{message}</span> : null}
      </div>
    </form>
  );
}

export function ProductForm({ brands }: { brands: Brand[] }) {
  const router = useRouter();
  const [message, setMessage] = useState<string | null>(null);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    await api.createProduct({
      brand_id: String(form.get("brand_id") || brands[0]?.id || ""),
      name: String(form.get("name") || ""),
      slug: String(form.get("slug") || ""),
      category: String(form.get("category") || ""),
      description: String(form.get("description") || ""),
      key_benefits: String(form.get("key_benefits") || "")
        .split(",")
        .map((item) => item.trim())
        .filter(Boolean),
      price_cents: Number(form.get("price_cents") || 0),
      active: true,
    });
    event.currentTarget.reset();
    setMessage("Product created.");
    router.refresh();
  }

  return (
    <form className="form" onSubmit={submit}>
      <div className="form-grid">
        <div className="field">
          <label htmlFor="brand_id">Brand</label>
          <select id="brand_id" name="brand_id" required>
            {brands.map((brand) => (
              <option key={brand.id} value={brand.id}>
                {brand.name}
              </option>
            ))}
          </select>
        </div>
        <div className="field">
          <label htmlFor="name">Product name</label>
          <input id="name" name="name" required />
        </div>
        <div className="field">
          <label htmlFor="slug">Slug</label>
          <input id="slug" name="slug" required />
        </div>
        <div className="field">
          <label htmlFor="category">Category</label>
          <input id="category" name="category" required />
        </div>
        <div className="field">
          <label htmlFor="price_cents">Price cents</label>
          <input id="price_cents" name="price_cents" type="number" min="0" />
        </div>
        <div className="field">
          <label htmlFor="key_benefits">Benefits</label>
          <input id="key_benefits" name="key_benefits" placeholder="เนียนนุ่ม, สะอาด, ฝุ่นน้อย" />
        </div>
      </div>
      <div className="field">
        <label htmlFor="description">Description</label>
        <textarea id="description" name="description" />
      </div>
      <div className="actions">
        <button type="submit">
          <Save size={16} aria-hidden="true" />
          Add Product
        </button>
        {message ? <span className="muted">{message}</span> : null}
      </div>
    </form>
  );
}

export function CampaignForm({ brands }: { brands: Brand[] }) {
  const router = useRouter();

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const campaign = await api.createCampaign({
      brand_id: String(form.get("brand_id") || brands[0]?.id || ""),
      name: String(form.get("name") || ""),
      objective: String(form.get("objective") || ""),
      status: String(form.get("status") || "draft"),
      start_date: String(form.get("start_date") || "") || null,
      end_date: String(form.get("end_date") || "") || null,
      target_audience: String(form.get("target_audience") || ""),
    });
    router.push(`/campaigns/${campaign.id}`);
    router.refresh();
  }

  return (
    <form className="form" onSubmit={submit}>
      <div className="form-grid">
        <div className="field">
          <label htmlFor="brand_id">Brand</label>
          <select id="brand_id" name="brand_id" required>
            {brands.map((brand) => (
              <option key={brand.id} value={brand.id}>
                {brand.name}
              </option>
            ))}
          </select>
        </div>
        <div className="field">
          <label htmlFor="name">Campaign name</label>
          <input id="name" name="name" required />
        </div>
        <div className="field">
          <label htmlFor="status">Status</label>
          <select id="status" name="status" defaultValue="draft">
            <option value="draft">Draft</option>
            <option value="active">Active</option>
            <option value="completed">Completed</option>
          </select>
        </div>
        <div className="field">
          <label htmlFor="target_audience">Audience</label>
          <input id="target_audience" name="target_audience" />
        </div>
        <div className="field">
          <label htmlFor="start_date">Start date</label>
          <input id="start_date" name="start_date" type="date" />
        </div>
        <div className="field">
          <label htmlFor="end_date">End date</label>
          <input id="end_date" name="end_date" type="date" />
        </div>
      </div>
      <div className="field">
        <label htmlFor="objective">Objective</label>
        <textarea id="objective" name="objective" required />
      </div>
      <button type="submit">
        <Save size={16} aria-hidden="true" />
        Create Campaign
      </button>
    </form>
  );
}

export function CsvImportForm() {
  const [fileName, setFileName] = useState("No file selected");

  return (
    <form className="form">
      <div className="field">
        <label htmlFor="csv">CSV import</label>
        <input
          id="csv"
          name="csv"
          type="file"
          accept=".csv"
          onChange={(event) => setFileName(event.target.files?.[0]?.name ?? "No file selected")}
        />
      </div>
      <div className="actions">
        <button type="button" className="secondary">
          <Upload size={16} aria-hidden="true" />
          Import Preview
        </button>
        <span className="muted">{fileName}</span>
      </div>
    </form>
  );
}

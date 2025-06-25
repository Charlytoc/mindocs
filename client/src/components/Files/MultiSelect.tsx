import React, { useState, useRef, useEffect } from "react";

interface Option {
  label: string;
  value: string;
}

interface MultiSelectProps {
  options: Option[];
  selectedValues: string[];
  onChange: (selectedValues: string[]) => void;
  placeholder?: string;
  disabled?: boolean;
  className?: string;
}

const MultiSelect: React.FC<MultiSelectProps> = ({
  options,
  selectedValues,
  onChange,
  placeholder = "Select options...",
  disabled = false,
  className = "",
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false);
        setSearchTerm("");
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const filteredOptions = options.filter((option) =>
    option.label.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleOptionToggle = (value: string) => {
    const newSelectedValues = selectedValues.includes(value)
      ? selectedValues.filter((v) => v !== value)
      : [...selectedValues, value];
    onChange(newSelectedValues);
  };

  const handleClearAll = () => {
    onChange([]);
  };

  const selectedCount = selectedValues.length;

  return (
    <div className={`relative ${className}`} ref={dropdownRef}>
      {/* Main input */}
      <div
        className={`
          relative w-full border border-gray-300 rounded-md px-3 py-2 cursor-pointer
          ${
            disabled
              ? "bg-gray-100 cursor-not-allowed"
              : "bg-white hover:border-gray-400"
          }
          ${isOpen ? "border-blue-500 ring-1 ring-blue-500" : ""}
        `}
        onClick={() => !disabled && setIsOpen(!isOpen)}
      >
        <div className="flex items-center justify-between">
          <div className="flex-1 min-w-0">
            {selectedCount > 0 ? (
              <div className="flex flex-wrap gap-1">
                {selectedValues.slice(0, 2).map((value) => {
                  const option = options.find((opt) => opt.value === value);
                  return (
                    <span
                      key={value}
                      className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
                    >
                      {option?.label}
                      <button
                        type="button"
                        className="ml-1 inline-flex items-center justify-center w-4 h-4 rounded-full text-blue-400 hover:bg-blue-200 hover:text-blue-500"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleOptionToggle(value);
                        }}
                      >
                        ×
                      </button>
                    </span>
                  );
                })}
                {selectedCount > 2 && (
                  <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-600">
                    +{selectedCount - 2} more
                  </span>
                )}
              </div>
            ) : (
              <span className="text-gray-500">{placeholder}</span>
            )}
          </div>
          <div className="flex items-center space-x-2">
            {selectedCount > 0 && (
              <button
                type="button"
                className="text-gray-400 hover:text-gray-600"
                onClick={(e) => {
                  e.stopPropagation();
                  handleClearAll();
                }}
              >
                ×
              </button>
            )}
            <svg
              className={`w-4 h-4 text-gray-400 transition-transform ${
                isOpen ? "rotate-180" : ""
              }`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M19 9l-7 7-7-7"
              />
            </svg>
          </div>
        </div>
      </div>

      {/* Dropdown */}
      {isOpen && !disabled && (
        <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-md shadow-lg max-h-60 overflow-hidden">
          {/* Search input */}
          <div className="p-2 border-b border-gray-200">
            <input
              type="text"
              placeholder="Search options..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              onClick={(e) => e.stopPropagation()}
            />
          </div>

          {/* Options list */}
          <div className="max-h-48 overflow-y-auto">
            {filteredOptions.length > 0 ? (
              filteredOptions.map((option) => (
                <div
                  key={option.value}
                  className={`
                    flex items-center px-3 py-2 cursor-pointer hover:bg-gray-50
                    ${selectedValues.includes(option.value) ? "bg-blue-50" : ""}
                  `}
                  onClick={(e) => {
                    e.stopPropagation();
                    handleOptionToggle(option.value);
                  }}
                >
                  <input
                    type="checkbox"
                    checked={selectedValues.includes(option.value)}
                    onChange={() => handleOptionToggle(option.value)}
                    className="mr-3 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    onClick={(e) => e.stopPropagation()}
                  />
                  <span className="text-sm text-gray-900">{option.label}</span>
                </div>
              ))
            ) : (
              <div className="px-3 py-2 text-sm text-gray-500">
                No options found
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default MultiSelect;

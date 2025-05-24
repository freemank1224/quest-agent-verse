
import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { cn } from '@/lib/utils';
import { useAuth } from '@/contexts/AuthContext';
import { useChat } from '@/contexts/ChatContext';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { LogOut, User, Lock } from 'lucide-react';
import { toast } from '@/components/ui/sonner';

const Navbar: React.FC = () => {
  const location = useLocation();
  const { user, profile, signOut } = useAuth();
  const { hasCourseGenerated } = useChat();

  // 处理受限页面的点击事件
  const handleRestrictedPageClick = (e: React.MouseEvent, pageName: string) => {
    if (!hasCourseGenerated) {
      e.preventDefault();
      toast.error(`请先在首页输入学习主题生成课程，然后才能访问${pageName}页面`);
    }
  };
  
  return (
    <nav className="bg-white shadow-sm border-b border-gray-100">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex">
            <div className="flex-shrink-0 flex items-center">
              <Link to="/" className="font-display text-xl font-bold text-primary">
                智能学习助手
              </Link>
            </div>
            <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
              <Link
                to="/"
                className={cn(
                  "inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium transition-colors",
                  location.pathname === "/"
                    ? "border-primary text-gray-900"
                    : "border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700"
                )}
              >
                首页
              </Link>
              
              {/* 课程规划页面 - 条件性启用 */}
              {hasCourseGenerated ? (
                <Link
                  to="/course-planning"
                  className={cn(
                    "inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium transition-colors",
                    location.pathname === "/course-planning"
                      ? "border-primary text-gray-900"
                      : "border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700"
                  )}
                >
                  课程规划
                </Link>
              ) : (
                <button
                  onClick={(e) => handleRestrictedPageClick(e, "课程规划")}
                  className="inline-flex items-center px-1 pt-1 border-b-2 border-transparent text-sm font-medium text-gray-400 cursor-not-allowed transition-colors"
                  disabled
                >
                  <Lock className="w-3 h-3 mr-1" />
                  课程规划
                </button>
              )}
              
              {/* 互动学习页面 - 条件性启用 */}
              {hasCourseGenerated ? (
                <Link
                  to="/interactive-learning"
                  className={cn(
                    "inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium transition-colors",
                    location.pathname === "/interactive-learning"
                      ? "border-primary text-gray-900"
                      : "border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700"
                  )}
                >
                  互动学习
                </Link>
              ) : (
                <button
                  onClick={(e) => handleRestrictedPageClick(e, "互动学习")}
                  className="inline-flex items-center px-1 pt-1 border-b-2 border-transparent text-sm font-medium text-gray-400 cursor-not-allowed transition-colors"
                  disabled
                >
                  <Lock className="w-3 h-3 mr-1" />
                  互动学习
                </button>
              )}
            </div>
          </div>
          
          <div className="flex items-center">
            {user ? (
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" className="relative h-8 w-8 rounded-full">
                    <Avatar className="h-8 w-8">
                      <AvatarImage src={profile?.avatar_url || undefined} alt={profile?.username || user.email || "用户"} />
                      <AvatarFallback className="bg-primary/10 text-primary">
                        {profile?.username?.charAt(0)?.toUpperCase() || user.email?.charAt(0)?.toUpperCase() || '?'}
                      </AvatarFallback>
                    </Avatar>
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent className="w-56" align="end" forceMount>
                  <div className="flex flex-col space-y-1 leading-none p-2">
                    <p className="font-medium">{profile?.username || '用户'}</p>
                    <p className="text-xs text-muted-foreground">{user.email}</p>
                  </div>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem asChild>
                    <Link to="/profile" className="flex w-full cursor-pointer items-center">
                      <User className="mr-2 h-4 w-4" />
                      <span>个人资料</span>
                    </Link>
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem
                    className="cursor-pointer"
                    onClick={() => signOut()}
                  >
                    <LogOut className="mr-2 h-4 w-4" />
                    <span>退出登录</span>
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            ) : (
              <Link to="/auth">
                <Button variant="default" size="sm">
                  登录 / 注册
                </Button>
              </Link>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
